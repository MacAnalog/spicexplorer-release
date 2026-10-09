import { describe, expect, it } from "vitest";
import { isCorsAllowedOrigin } from "./api";

// `isCorsAllowedOrigin` mirrors the API's CORS policy, which is the hard limit on the
// direct-to-backend SSE lane (see the long note in api.ts). The source of truth is the
// platform:
//
//   packages/spicexplorer-api/src/spicexplorer_api/main.py
//     allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?"
//
// These cases were confirmed against a live API by sending each Origin to /health and
// checking for an `access-control-allow-origin` header in the response.
//
// NOTE: this pins the UI's *mirror*. It cannot detect drift in the platform's regex —
// CORS is not part of the OpenAPI contract, so the type-drift check does not see it
// either. If the platform policy changes, this file and the api.ts note must follow.
describe("isCorsAllowedOrigin", () => {
  it("accepts loopback origins on any port", () => {
    expect(isCorsAllowedOrigin("http://localhost:4000")).toBe(true);
    expect(isCorsAllowedOrigin("http://localhost:8000")).toBe(true);
    expect(isCorsAllowedOrigin("http://127.0.0.1:4000")).toBe(true);
    expect(isCorsAllowedOrigin("http://localhost")).toBe(true);
    expect(isCorsAllowedOrigin("http://127.0.0.1")).toBe(true);
  });

  it("rejects LAN origins — the documented reason SSE cannot work off loopback", () => {
    expect(isCorsAllowedOrigin("http://192.168.1.50:4000")).toBe(false);
    expect(isCorsAllowedOrigin("http://10.0.0.7:4000")).toBe(false);
    expect(isCorsAllowedOrigin("http://somehost:4000")).toBe(false);
    expect(isCorsAllowedOrigin("http://somehost.local:4000")).toBe(false);
  });

  it("rejects https, even on loopback", () => {
    expect(isCorsAllowedOrigin("https://localhost:4000")).toBe(false);
    expect(isCorsAllowedOrigin("https://127.0.0.1:4000")).toBe(false);
  });

  it("is anchored — a loopback-looking substring does not pass", () => {
    expect(isCorsAllowedOrigin("http://localhost.evil.com:4000")).toBe(false);
    expect(isCorsAllowedOrigin("http://notlocalhost:4000")).toBe(false);
    expect(isCorsAllowedOrigin("http://127.0.0.1:4000/path")).toBe(false);
  });
});
