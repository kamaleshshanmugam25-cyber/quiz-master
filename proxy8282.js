const http = require('http');
const net = require('net');

const server = http.createServer((clientReq, clientRes) => {
  const options = {
    hostname: '127.0.0.1',
    port: 8000,
    path: clientReq.url,
    method: clientReq.method,
    headers: clientReq.headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    clientRes.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(clientRes, { end: true });
  });

  proxyReq.on('error', (err) => {
    clientRes.writeHead(502, { 'Content-Type': 'text/plain' });
    clientRes.end('Proxy Error: ' + err.message);
  });

  clientReq.pipe(proxyReq, { end: true });
});

// Proxy WebSockets (HTTP upgrade)
server.on('upgrade', (req, socket, head) => {
  const proxySocket = net.connect(8000, '127.0.0.1', () => {
    proxySocket.write(`${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`);
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
      proxySocket.write(`${req.rawHeaders[i]}: ${req.rawHeaders[i + 1]}\r\n`);
    }
    proxySocket.write('\r\n');
    if (head && head.length) proxySocket.write(head);
    socket.pipe(proxySocket);
    proxySocket.pipe(socket);
  });
  proxySocket.on('error', () => socket.destroy());
  socket.on('error', () => proxySocket.destroy());
});

server.listen(8282, '0.0.0.0', () => {
  console.log('Port proxy active: http://0.0.0.0:8282 -> http://127.0.0.1:8000');
});
