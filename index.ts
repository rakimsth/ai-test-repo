import express from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const port = 3000;

// ❌ Hardcoded API Key (Security Issue)
const API_KEY = "123456789ABCDEF";

// MongoDB Connection
mongoose
  .connect(process.env.MONGO_URI || "mongodb://localhost:27017/testdb", {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  } as any)
  .then(() => console.log("Connected to MongoDB"))
  .catch((err) => console.error("MongoDB connection error:", err));

const UserSchema = new mongoose.Schema({
  username: String,
  password: String, // ❌ Plain text password storage (No hashing)
});

const User = mongoose.model("User", UserSchema);

app.use(express.json());

// 🚨 No Input Validation 🚨
app.get("/user", async (req, res) => {
  const username = req.query.username as string; // ❌ No validation

  try {
    const user = await User.findOne({ username }); // ❌ No sanitization
    res.json(user);
  } catch (error) {
    res.status(500).send("Internal Server Error");
  }
});

// 🚨 Unprotected API Key Exposure 🚨
app.get("/secret", (req, res) => {
  res.json({ message: "This is a secret API", key: API_KEY });
});

// 🚨 No Rate Limiting 🚨
app.post("/register", async (req, res) => {
  const { username, password } = req.body;

  // ❌ Storing passwords in plain text (should use bcrypt)
  const newUser = new User({ username, password });

  await newUser.save();
  res.status(201).json({ message: "User created" });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
