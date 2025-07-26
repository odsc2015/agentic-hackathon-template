const { runAsync, getAsync, allAsync } = require('../config/db');
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');

class User {
  static async create(email, username, password) {
    const id = uuidv4();
    const passwordHash = await bcrypt.hash(password, 10);
    
    await runAsync(
      'INSERT INTO users (id, email, username, password_hash) VALUES (?, ?, ?, ?)',
      [id, email, username, passwordHash]
    );
    
    return { id, email, username };
  }
  
  static async findByEmail(email) {
    return await getAsync('SELECT * FROM users WHERE email = ?', [email]);
  }
  
  static async findById(id) {
    const user = await getAsync('SELECT * FROM users WHERE id = ?', [id]);
    if (user) {
      delete user.password_hash; // Don't send password hash
    }
    return user;
  }
  
  static async verifyPassword(email, password) {
    const user = await this.findByEmail(email);
    if (!user) return null;
    
    const isValid = await bcrypt.compare(password, user.password_hash);
    if (!isValid) return null;
    
    delete user.password_hash;
    return user;
  }
}

module.exports = User;