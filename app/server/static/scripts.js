// Wait for Chart.js to load before initializing charts
document.addEventListener('DOMContentLoaded', async function () {
  // Fetch the schemas from the endpoints
  const [statsSchemaResponse] = await Promise.all([
    fetch('/api/1.0.0/data-schema'),
  ]);
  const statsSchema = await statsSchemaResponse.json();

  // Function to validate event against schema
  function validateAgainstSchema(event, schema) {
    // Basic validation of required fields and types
    if (schema.data_schema.required) {
      for (const field of schema.data_schema.required) {
        if (!(field in event)) {
          throw new Error(`Missing required field: ${field}`);
        }
      }
    }

    // Validate properties according to schema
    for (const [key, value] of Object.entries(event)) {
      const propertySchema = schema.data_schema.properties[key];
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

  // Open Websocket connection
  var socket = new WebSocket('ws://localhost:8000/api/1.0.0/ws/stats');

  // On open function
  socket.onopen = function (event) {
    socket.send(
      JSON.stringify({ event: 'CONNECT', client: 'SERVER-STATS' })
    );
  };

  // Setting up HTML Elements
  let cpu_count = document.getElementById('cpu_count');
  let cpu_usage = document.getElementById('cpu_usage');
  let cpu_frequency = document.getElementById('cpu_frequency');
  let core_temperature = document.getElementById('core_temperature');
  let ram_total = document.getElementById('ram_total');
  let ram_availble = document.getElementById('ram_available');
  let ram_percentage = document.getElementById('ram_percentage');
  let disk_total = document.getElementById('disk_total');
  let disk_free = document.getElementById('disk_free');
  let disk_used = document.getElementById('disk_used');
  let disk_percentage = document.getElementById('disk_percentage');

  // Main Websocket Communication
  socket.onmessage = function (event) {
    let data = JSON.parse(event.data);
    console.log(data);
    if (data.data) {
      if (data.event === 'data-request') {
        try {
          validateAgainstSchema(data.data, statsSchema);
          updateData(data.data);
        } catch (err) {
          console.error('Schema validation failed:', err);
        }
      }
    }
  };

  // Chart configs
  let numberElements = 120;

  //Globals
  let updateCount = 0;

  // Chart Objects
  let cpuUsageChart = document.getElementById('cpuUsage');
  let ramUsageChart = document.getElementById('ramUsage');
  let diskUsageChart = document.getElementById('diskUsage');

  // Common Chart Options (Line)
  let commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    backgroundColor: 'rgba(33,31,51,0.5)',
    borderColor: 'rgba(33,31,51,1)',
    fill: true,
    scales: {
      x: {
        color: 'black',
        grid: {
          display: false,
        },
        ticks: {
          color: 'black',
        },
      },
      y: {
        beginAtZero: true,
        max: 100,
        grid: {
          color: 'rgba(33,31,51,0.2)',
        },
        ticks: {
          color: 'black',
        },
      },
    },
    legend: { display: false },
    tooltips: {
      enabled: false,
    },
  };

  // cpuUsageChart Instance
  var cpuUsageChartInstance = new Chart(cpuUsageChart, {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'CPU Usage',
          data: 0,
          borderWidth: 1,
        },
      ],
    },
    options: Object.assign({}, commonOptions, {
      responsive: true,
      title: {
        display: true,
        text: 'CPU Usage',
        fontSize: 18,
      },
    }),
  });

  // ramUsageChart Instance
  var ramUsageChartInstance = new Chart(ramUsageChart, {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'RAM Usage',
          data: 0,
          borderWidth: 1,
        },
      ],
    },
    options: Object.assign({}, commonOptions, {
      title: {
        display: true,
        text: 'RAM Usage',
        fontSize: 18,
      },
    }),
  });

  // diskUsageChart Instance
  var diskUsageChartInstance = new Chart(diskUsageChart, {
    type: 'doughnut',
    responsive: false,
    maintainAspectRatio: false,
    labels: ['free', 'Used'],
    data: {
      datasets: [
        {
          label: 'Disk Usage',
          data: [1, 1],
          backgroundColor: [
            'rgba(189, 27, 15, .8)',
            'rgba(33, 31, 81, .9)',
          ],
          hoverOffset: 4,
        },
      ],
    },
    options: Object.assign(
      {},
      {
        title: {
          display: true,
          text: 'Disk Usage',
          fontSize: 18,
        },
      }
    ),
  });

  // Function to push data to chart object instances
  function addData(data) {
    if (!data) return;

    try {
      let today = new Date();
      let time =
        today.getMinutes() < 10
          ? `${today.getHours()}:0${today.getMinutes()}`
          : `${today.getHours()}:${today.getMinutes()}`;

      // Initialize datasets if needed
      if (!cpuUsageChartInstance.data.datasets[0].data) {
        cpuUsageChartInstance.data.datasets[0].data = [];
      }
      if (!ramUsageChartInstance.data.datasets[0].data) {
        ramUsageChartInstance.data.datasets[0].data = [];
      }
      if (!cpuUsageChartInstance.data.labels) {
        cpuUsageChartInstance.data.labels = [];
      }
      if (!ramUsageChartInstance.data.labels) {
        ramUsageChartInstance.data.labels = [];
      }

      // CPU Usage
      cpuUsageChartInstance.data.labels.push(time);
      cpuUsageChartInstance.data.datasets[0].data.push(
        data.cpu_usage
      );

      // RAM Usage
      ramUsageChartInstance.data.labels.push(time);
      ramUsageChartInstance.data.datasets[0].data.push(
        data.ram_percentage
      );

      // Disk Usage
      diskUsageChartInstance.data.datasets[0].data = [
        data.disk_used,
        data.disk_free,
      ];

      if (updateCount > numberElements) {
        // For shifting the x axis markers
        cpuUsageChartInstance.data.labels.shift();
        cpuUsageChartInstance.data.datasets[0].data.shift();
        ramUsageChartInstance.data.labels.shift();
        ramUsageChartInstance.data.datasets[0].data.shift();
      } else {
        updateCount++;
      }

      cpuUsageChartInstance.update();
      ramUsageChartInstance.update();
      diskUsageChartInstance.update();
    } catch (err) {
      console.error('Error updating charts:', err);
    }
  }

  // Update HTML elements
  function updateData(data) {
    if (!data) return;

    try {
      addData(data);

      cpu_count.innerHTML = `Core count: ${data.cpu_count}`;
      cpu_usage.innerHTML = `CPU usage: ${data.cpu_usage}%`;
      cpu_frequency.innerHTML = `CPU Frequency: ${data.cpu_frequency.current_frequency} GHz`;
      ram_total.innerHTML = `RAM total: ${data.ram_total} GB`;
      ram_available.innerHTML = `RAM Available: ${data.ram_available} GB`;
      ram_percentage.innerHTML = `Percentage of RAM used: ${data.ram_percentage}%`;
      disk_total.innerHTML = `Disk space total: ${data.disk_total} GB`;
      disk_free.innerHTML = `Disk Space Free: ${data.disk_free} GB`;
      disk_used.innerHTML = `Disk Space used: ${data.disk_used} GB`;
      disk_percentage.innerHTML = `Disk Space Used: ${data.disk_percentage}%`;
    } catch (err) {
      console.error('Error updating stats:', err);
    }
  }
}); // End of DOMContentLoaded
