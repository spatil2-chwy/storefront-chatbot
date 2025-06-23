const { spawn } = require('child_process');
const path = require('path');

// Start the backend server
const backend = spawn('npx', ['tsx', 'server/index.ts'], {
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'development' }
});

// Start the frontend dev server
const frontend = spawn('npm', ['run', 'dev'], {
  cwd: path.join(__dirname, 'client'),
  stdio: 'inherit',
  env: { ...process.env, PORT: '3000' }
});

// Handle process termination
process.on('SIGINT', () => {
  backend.kill();
  frontend.kill();
  process.exit();
});

backend.on('exit', (code) => {
  console.log(`Backend exited with code ${code}`);
  frontend.kill();
});

frontend.on('exit', (code) => {
  console.log(`Frontend exited with code ${code}`);
  backend.kill();
});