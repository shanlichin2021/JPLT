// backend/build-database.js
import fs from 'fs';
import { XMLParser } from 'fast-xml-parser';
import sqlite3 from 'sqlite3';

const JMDictPath = './JMdict_e/JMdict_e.xml'; // Make sure it has the .xml extension
const dbPath = './dictionary.sqlite';

console.log("Starting dictionary build process...");

if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
    console.log("Removed old database file.");
}
const db = new sqlite3.Database(dbPath);

console.log("Reading JMdict file (this may take a moment)...");
const xmlData = fs.readFileSync(JMDictPath, 'utf8');
const parser = new XMLParser();
const jmdict = parser.parse(xmlData);
console.log(`JMdict file parsed. Found ${jmdict.JMdict.entry.length} entries.`);

db.serialize(() => {
    console.log("Creating database schema...");
    db.run(`CREATE TABLE entries (id INTEGER PRIMARY KEY, ent_seq TEXT NOT NULL UNIQUE);`);
    db.run(`CREATE TABLE kanji (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER, value TEXT NOT NULL, FOREIGN KEY (entry_id) REFERENCES entries(id));`);
    db.run(`CREATE TABLE reading (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER, value TEXT NOT NULL, FOREIGN KEY (entry_id) REFERENCES entries(id));`);
    db.run(`CREATE TABLE sense (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER, pos TEXT, gloss TEXT, FOREIGN KEY (entry_id) REFERENCES entries(id));`);
    
    console.log("Schema created. Preparing statements for data insertion...");
    const entryStmt = db.prepare("INSERT INTO entries (ent_seq) VALUES (?)");
    const kanjiStmt = db.prepare("INSERT INTO kanji (entry_id, value) VALUES (?, ?)");
    const readingStmt = db.prepare("INSERT INTO reading (entry_id, value) VALUES (?, ?)");
    const senseStmt = db.prepare("INSERT INTO sense (entry_id, pos, gloss) VALUES (?, ?, ?)");

    console.log("Starting transaction to insert all entries...");
    db.run("BEGIN TRANSACTION");

    let entryIdCounter = 1;
    for (const entry of jmdict.JMdict.entry) {
        entryStmt.run(entry.ent_seq);
        const entryId = entryIdCounter++;

        if (entry.k_ele) {
            const elements = Array.isArray(entry.k_ele) ? entry.k_ele : [entry.k_ele];
            for (const k of elements) {
                if(k && k.keb) kanjiStmt.run(entryId, k.keb);
            }
        }

        if (entry.r_ele) {
            const elements = Array.isArray(entry.r_ele) ? entry.r_ele : [entry.r_ele];
            for (const r of elements) {
                if(r && r.reb) readingStmt.run(entryId, r.reb);
            }
        }
        
        if (entry.sense) {
            const senses = Array.isArray(entry.sense) ? entry.sense : [entry.sense];
            for (const s of senses) {
                // --- REVISED AND MORE ROBUST LOGIC START ---
                
                // Ensure partsOfSpeech is always a string
                const partsOfSpeech = s.pos ? (Array.isArray(s.pos) ? s.pos.join(', ') : String(s.pos)) : '';

                // Safely extract definitions and ensure it's always a JSON array string
                let definitions = [];
                if (s.gloss) {
                    const glossElements = Array.isArray(s.gloss) ? s.gloss : [s.gloss];
                    definitions = glossElements.map(g => {
                        // The parser might return an object {'#text': '...'} or just a string
                        return (typeof g === 'object' && g['#text']) ? g['#text'] : String(g);
                    });
                }
                const glossesJson = JSON.stringify(definitions);

                // This statement is now much safer and will not receive undefined values
                senseStmt.run(entryId, partsOfSpeech, glossesJson);
                
                // --- REVISED AND MORE ROBUST LOGIC END ---
            }
        }

        if (entryId % 10000 === 0) {
            console.log(`...processed ${entryId} / ${jmdict.JMdict.entry.length} entries...`);
        }
    }

    console.log("Finalizing insertions...");
    entryStmt.finalize();
    kanjiStmt.finalize();
    readingStmt.finalize();
    senseStmt.finalize();
    db.run("COMMIT");

    console.log("Database build complete! Creating indexes for faster lookups...");
    db.run("CREATE INDEX idx_kanji_value ON kanji(value)");
    db.run("CREATE INDEX idx_reading_value ON reading(value)");
    
    db.close((err) => {
        if (err) {
            console.error(err.message);
            return;
        }
        console.log("✅ Success! 'dictionary.sqlite' has been created.");
    });
});