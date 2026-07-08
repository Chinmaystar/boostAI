import { verify } from "hono/jwt";
import type { Context, Next } from "hono";
import { config } from "../config.js";

export interface JwtPayload {
  userId: number;
  email: string;
  role: "school" | "univ";
}

export async function authGuard(c: Context, next: Next) {
  const header = c.req.header("Authorization");
  if (!header || !header.startsWith("Bearer ")) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  try {
    const token = header.slice(7);
    const payload = await verify(token, config.JWT_SECRET, "HS256") as unknown as JwtPayload;
    c.set("jwtPayload", payload);
    await next();
  } catch {
    return c.json({ error: "Invalid or expired token" }, 401);
  }
}
