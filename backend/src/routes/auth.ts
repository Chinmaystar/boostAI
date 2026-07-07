import { Hono } from "hono";
import { sign } from "hono/jwt";
import { eq } from "drizzle-orm";
import bcrypt from "bcryptjs";
import { createRemoteJWKSet, jwtVerify } from "jose";
import { db } from "../db/index.js";
import { users } from "../db/schema.js";
import { config } from "../config.js";
import { authGuard, type JwtPayload } from "../middleware/auth.js";

const auth = new Hono();

const googleJWKS = createRemoteJWKSet(new URL("https://www.googleapis.com/oauth2/v3/certs"));

auth.post("/signup", async (c) => {
  const { email, password, role } = await c.req.json();

  if (!email || !password || !role) {
    return c.json({ error: "Email, password, and role are required" }, 400);
  }

  if (!["school", "univ"].includes(role)) {
    return c.json({ error: "Role must be 'school' or 'univ'" }, 400);
  }

  if (password.length < 6) {
    return c.json({ error: "Password must be at least 6 characters" }, 400);
  }

  const existing = await db.select().from(users).where(eq(users.email, email)).limit(1);
  if (existing.length > 0) {
    return c.json({ error: "Email already registered" }, 409);
  }

  const passwordHash = await bcrypt.hash(password, 10);
  const [user] = await db.insert(users).values({ email, passwordHash, role }).returning();

  const token = await sign({ userId: user.id, email: user.email, role: user.role }, config.JWT_SECRET);

  return c.json({ token, user: { id: user.id, email: user.email, role: user.role } });
});

auth.post("/login", async (c) => {
  const { email, password } = await c.req.json();

  if (!email || !password) {
    return c.json({ error: "Email and password are required" }, 400);
  }

  const [user] = await db.select().from(users).where(eq(users.email, email)).limit(1);
  if (!user) {
    return c.json({ error: "Invalid email or password" }, 401);
  }

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) {
    return c.json({ error: "Invalid email or password" }, 401);
  }

  const token = await sign({ userId: user.id, email: user.email, role: user.role }, config.JWT_SECRET);

  return c.json({ token, user: { id: user.id, email: user.email, role: user.role } });
});

auth.post("/google/callback", async (c) => {
  const { code, role } = await c.req.json();

  if (!code) {
    return c.json({ error: "Authorization code is required" }, 400);
  }

  let idToken: string;
  try {
    const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        code,
        client_id: config.GOOGLE_CLIENT_ID,
        client_secret: config.GOOGLE_CLIENT_SECRET,
        redirect_uri: "http://localhost:3000",
        grant_type: "authorization_code",
      }),
    });

    if (!tokenRes.ok) {
      const errText = await tokenRes.text();
      console.error("Google token exchange failed:", errText);
      return c.json({ error: "Failed to exchange authorization code" }, 401);
    }

    const tokenData = await tokenRes.json();
    idToken = tokenData.id_token;
  } catch (err) {
    console.error("Google token exchange error:", err);
    return c.json({ error: "Failed to exchange authorization code" }, 401);
  }

  let payload;
  try {
    const result = await jwtVerify(idToken, googleJWKS, {
      issuer: ["accounts.google.com", "https://accounts.google.com"],
      audience: config.GOOGLE_CLIENT_ID,
    });
    payload = result.payload;
  } catch {
    return c.json({ error: "Invalid Google ID token" }, 401);
  }

  const email = payload.email as string;
  if (!email) {
    return c.json({ error: "Google account has no email" }, 400);
  }

  const [existing] = await db.select().from(users).where(eq(users.email, email)).limit(1);
  if (existing) {
    const token = await sign({ userId: existing.id, email: existing.email, role: existing.role }, config.JWT_SECRET);
    return c.json({ token, user: { id: existing.id, email: existing.email, role: existing.role } });
  }

  const userRole = role === "school" ? "school" : "univ";
  const [user] = await db.insert(users).values({
    email,
    passwordHash: "",
    role: userRole,
  }).returning();

  const token = await sign({ userId: user.id, email: user.email, role: user.role }, config.JWT_SECRET);
  return c.json({ token, user: { id: user.id, email: user.email, role: user.role } });
});

auth.get("/me", authGuard, async (c) => {
  const payload = c.get("jwtPayload") as JwtPayload;
  const [user] = await db.select().from(users).where(eq(users.id, payload.userId)).limit(1);
  if (!user) {
    return c.json({ error: "User not found" }, 404);
  }
  return c.json({ id: user.id, email: user.email, role: user.role });
});

export default auth;
