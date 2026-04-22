import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@olho/db";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is not set");
}

const client = postgres(connectionString, {
  max: 10,
  idle_timeout: 20,
});

export const db = drizzle(client, { schema });
export type DB = typeof db;
