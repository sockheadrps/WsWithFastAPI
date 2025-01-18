document.addEventListener("DOMContentLoaded", async function () {
  // Fetch the schemas from the endpoints
  const [pingSchemaResponse, pingResponseSchemaResponse] = await Promise.all([
      fetch('/ping-schema'),
      fetch('/ping-response-schema')
  ]);
  const pingEventSchema = await pingSchemaResponse.json();
  const pingResponseSchema = await pingResponseSchemaResponse.json();

  // Function to validate event against schema
  function validateAgainstSchema(event, schema) {
      // Basic validation of required fields and types
      if (schema.required) {
          for (const field of schema.required) {
              if (!(field in event)) {
                  throw new Error(`Missing required field: ${field}`);
              }
          }
      }

      // Validate properties according to schema
      for (const [key, value] of Object.entries(event)) {
          const propertySchema = schema.properties[key];
          if (propertySchema && propertySchema.type) {
              const type = typeof value;
              if (propertySchema.type === 'string' && type !== 'string') {
                  throw new Error(`${key} must be a string`);
              }
              if (propertySchema.type === 'object' && type !== 'object') {
                  throw new Error(`${key} must be an object`);
              }
          }
      }
      return true;
  }

  // Create container for client cards
  const clientsContainer = document.createElement('div');
  clientsContainer.id = 'clients-container';
  document.body.appendChild(clientsContainer);

  // Track ping timestamps
  const pingTimestamps = new Map();

  // Function to create/update client cards
  function updateClientCards(pyClients) {
      clientsContainer.innerHTML = ''; // Clear existing cards
      
      pyClients.forEach(clientId => {
          const card = document.createElement('div');
          card.className = 'client-card';
          card.style.border = '1px solid #ccc';
          card.style.padding = '10px';
          card.style.margin = '10px';
          card.style.borderRadius = '5px';

          const idText = document.createElement('p');
          idText.textContent = `Client ID: ${clientId}`;
          
          const latencyText = document.createElement('p');
          latencyText.id = `latency-${clientId}`;
          latencyText.textContent = 'Latency: Not measured';
          
          const pingButton = document.createElement('button');
          pingButton.textContent = 'Ping';
          pingButton.onclick = () => {
              try {
                  const pingEvent = {
                      event: pingEventSchema.properties.event.const,
                      client_id: myClientId,
                      data: {
                          data: {
                              target_client_id: clientId
                          }
                      }
                  };

                  validateAgainstSchema(pingEvent, pingEventSchema);
                  pingTimestamps.set(clientId, Date.now());
                  socket.send(JSON.stringify(pingEvent));
                  console.log('Ping event sent:', pingEvent);
              } catch (error) {
                  console.error('Error sending ping event:', error);
              }
          };

          card.appendChild(idText);
          card.appendChild(latencyText);
          card.appendChild(pingButton);
          clientsContainer.appendChild(card);
      });
  }

  // WebSocket connection setup
  const socket = new WebSocket('ws://localhost:8000/ws/web_client');
  let myClientId = null;

  socket.onopen = () => {
      console.log('WebSocket connection established');
  };

  socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("Received from server:", message);

      if (message.event === "connect") {
          myClientId = message.client_id;
          console.log('Received client ID:', myClientId);
      } else if (message.event === "py_clients_update") {
          updateClientCards(message.data.data.py_clients);
      } else if (message.event === "ping_response") {
          try {
              validateAgainstSchema(message, pingResponseSchema);
              const targetClientId = message.client_id;
              const startTime = pingTimestamps.get(targetClientId);
              if (startTime) {
                  const latency = Date.now() - startTime;
                  
                  // calculate the latency as a ratio between 0 and 1, and then scale that to a color between green and red
                  const latencyRatio = Math.min(latency / 1000, 1); // Cap at 1
                  const red = Math.round(255 * latencyRatio);
                  const green = Math.round(255 * (1 - latencyRatio));
                  const latencyColor = `rgba(${red}, ${green}, 0, 0.5)`;
                  const latencyElement = document.getElementById(`latency-${targetClientId}`);
                  if (latencyElement) {
                      latencyElement.textContent = `Latency: ${latency}ms`;
                      latencyElement.parentElement.style.backgroundColor = latencyColor;
                  }
                  pingTimestamps.delete(targetClientId);
              }
          } catch (error) {
              console.error('Error processing ping response:', error);
          }
      }
  };

  socket.onclose = () => {
      console.log('WebSocket connection closed');
  };

  socket.onerror = (error) => {
      console.log('WebSocket error:', error);
  };
});
