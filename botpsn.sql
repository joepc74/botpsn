BEGIN TRANSACTION;
DROP TABLE IF EXISTS "busquedas";
CREATE TABLE "busquedas" (
	"id"	INTEGER,
	"sku"	TEXT NOT NULL,
	"store"	TEXT NOT NULL,
	"titulo"	TEXT NOT NULL DEFAULT 'Unknown',
	"precio"	REAL NOT NULL,
	"actualizado"	INTEGER NOT NULL DEFAULT (unixepoch()),
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "trackings";
CREATE TABLE "trackings" (
	"id"	INTEGER,
	"chatid"	TEXT NOT NULL,
	"sku"	TEXT NOT NULL,
	"preciomin"	REAL NOT NULL,
	"lang"	TEXT NOT NULL DEFAULT 'es',
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "usuarios";
CREATE TABLE "usuarios" (
	"id"	INTEGER,
	"chatid"	TEXT NOT NULL UNIQUE,
	"storedefault"	TEXT DEFAULT 'ESP',
	"searchstores"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
