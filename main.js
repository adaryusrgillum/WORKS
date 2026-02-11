const { app, BrowserWindow, dialog } = require("electron");
const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

let mainWindow = null;
let backendProcess = null;
let backendPort = 0;
let backendExitedEarly = false;
let backendExitDetail = "";

function backendLogPath() {
  return path.join(app.getPath("userData"), "backend.log");
}

function appendBackendLog(line) {
  try {
    const stamp = new Date().toISOString();
    fs.appendFileSync(backendLogPath(), `[${stamp}] ${line}\n`, "utf8");
  } catch (_) {}
}

function projectBaseDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "app_data");
  }
  return __dirname;
}

function findOpenPort(startPort = 8510, attempts = 30) {
  return new Promise((resolve, reject) => {
    let port = startPort;
    const net = require("net");

    const tryNext = () => {
      if (port >= startPort + attempts) {
        reject(new Error("No available port found for backend server."));
        return;
      }

      const server = net.createServer();
      server.once("error", () => {
        port += 1;
        tryNext();
      });
      server.once("listening", () => {
        server.close(() => resolve(port));
      });
      server.listen(port, "127.0.0.1");
    };

    tryNext();
  });
}

function streamlitCommandArgs(port) {
  return [
    "-m",
    "streamlit",
    "run",
    "streamlit_app.py",
    "--server.headless",
    "true",
    "--server.port",
    String(port),
    "--server.address",
    "127.0.0.1",
    "--browser.gatherUsageStats",
    "false"
  ];
}

function startBackendAtPort(baseDir, port) {
  return new Promise((resolve, reject) => {
    backendExitedEarly = false;
    backendExitDetail = "";
    const candidates = [
      { cmd: "py", args: ["-3.13", ...streamlitCommandArgs(port)] },
      { cmd: "py", args: ["-3", ...streamlitCommandArgs(port)] },
      { cmd: "python", args: streamlitCommandArgs(port) }
    ];

    const tryCandidate = (index) => {
      if (index >= candidates.length) {
        reject(
          new Error(
            "Could not launch Streamlit. Install Python 3.13+ and run `py -3.13 -m pip install -r requirements.txt`."
          )
        );
        return;
      }

      const c = candidates[index];
      appendBackendLog(`Launching backend candidate: ${c.cmd} ${c.args.join(" ")}`);
      const env = { ...process.env, ELECTRON_RUN_AS_NODE: "" };
      const child = spawn(c.cmd, c.args, {
        cwd: baseDir,
        windowsHide: true,
        shell: false,
        env
      });

      let stderrBuffer = "";
      let resolved = false;

      child.stdout.on("data", (data) => {
        appendBackendLog(`[stdout] ${data.toString().trim()}`);
      });

      child.stderr.on("data", (data) => {
        const chunk = data.toString();
        stderrBuffer += chunk;
        appendBackendLog(`[stderr] ${chunk.trim()}`);
      });

      child.on("error", (err) => {
        appendBackendLog(`Candidate failed to spawn: ${String(err)}`);
        tryCandidate(index + 1);
      });

      child.on("spawn", () => {
        backendProcess = child;
        resolved = true;
        appendBackendLog(`Backend process started. pid=${child.pid}`);
        resolve(child);
      });

      child.on("exit", (code) => {
        appendBackendLog(`Backend exited. code=${code}`);
        backendExitedEarly = true;
        backendExitDetail = stderrBuffer || `Backend exited with code ${code}.`;
        if (!resolved) {
          tryCandidate(index + 1);
          return;
        }
        if (code !== 0) {
          dialog.showErrorBox(
            "SEOBOT Backend Error",
            `${backendExitDetail}\n\nLog: ${backendLogPath()}`
          );
        }
      });
    };

    tryCandidate(0);
  });
}

function waitForBackend(port, timeoutMs = 120000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const url = `http://127.0.0.1:${port}`;

    const attempt = () => {
      if (backendExitedEarly) {
        reject(new Error(`Backend exited before ready. ${backendExitDetail}\nLog: ${backendLogPath()}`));
        return;
      }

      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode >= 200 && res.statusCode < 500) {
          appendBackendLog(`Backend is ready at ${url} (status=${res.statusCode})`);
          resolve(url);
        } else if (Date.now() - start > timeoutMs) {
          reject(new Error("Backend started but did not become ready."));
        } else {
          setTimeout(attempt, 500);
        }
      });

      req.on("error", () => {
        if (Date.now() - start > timeoutMs) {
          reject(new Error("Timed out waiting for backend server."));
        } else {
          setTimeout(attempt, 500);
        }
      });
      req.setTimeout(4000, () => {
        req.destroy();
      });
    };

    attempt();
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 920,
    minWidth: 1024,
    minHeight: 720,
    autoHideMenuBar: true,
    title: "SEOBOT"
  });

  mainWindow.loadURL(
    "data:text/html;charset=UTF-8," +
      encodeURIComponent(
        "<html><body style='font-family:Segoe UI, sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;background:#f6f9f8;color:#0f172a'><div><h2>SEOBOT is starting...</h2><p>Loading EPUB knowledge base service.</p></div></body></html>"
      )
  );
}

function stopBackend() {
  if (!backendProcess) return;

  const pid = backendProcess.pid;
  backendProcess = null;
  if (!pid) return;

  if (process.platform === "win32") {
    spawn("taskkill", ["/pid", String(pid), "/t", "/f"], { windowsHide: true });
  } else {
    process.kill(pid, "SIGTERM");
  }
}

async function bootstrap() {
  createWindow();
  const baseDir = projectBaseDir();
  backendPort = await findOpenPort();
  await startBackendAtPort(baseDir, backendPort);
  const url = await waitForBackend(backendPort);
  await mainWindow.loadURL(url);
}

app.whenReady().then(async () => {
  try {
    await bootstrap();
  } catch (err) {
    dialog.showErrorBox("SEOBOT Startup Error", String(err));
    app.quit();
  }
});

app.on("window-all-closed", () => {
  stopBackend();
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  stopBackend();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    bootstrap().catch((err) => {
      dialog.showErrorBox("SEOBOT Startup Error", String(err));
      app.quit();
    });
  }
});
