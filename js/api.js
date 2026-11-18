const localDevelopmentApi = ["localhost","127.0.0.1"].includes(location.hostname) && location.port === "8080";
const API = {
  base: window.SIMULATOR_API_BASE || (localDevelopmentApi ? "http://127.0.0.1:5000" : ""),
  async request(path, options = {}) {
    const config = {
      cache: "no-store",
      ...options,
      headers: {Accept:"application/json", ...(options.headers || {})}
    };
    if (options.body && !config.headers["Content-Type"]) {
      config.headers["Content-Type"] = "application/json";
    }
    let response;
    try {
      response = await fetch(this.base + path, config);
    } catch (error) {
      throw new Error(`Could not connect to the simulator API. Check the server and API address. (${error.message})`);
    }
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : {};
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    return data;
  },
  post(path, body) { return this.request(path, {method:"POST", body:JSON.stringify(body)}); },
  get(path) { return this.request(path); },
  delete(path) { return this.request(path, {method:"DELETE"}); }
};
