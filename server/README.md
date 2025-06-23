# Smart Pet Shopping Assistant - Backend

Express.js backend server for the Smart Pet Shopping Assistant, providing RESTful APIs for user authentication, product management, and real-time chat functionality.

## 🏗 Architecture

The backend follows a clean, modular architecture:

- **Express.js Server**: Main application server with middleware
- **Storage Layer**: Abstracted data storage with in-memory implementation
- **Route Handlers**: RESTful API endpoints
- **Type Safety**: Full TypeScript implementation with Zod validation
- **Development Setup**: Integrated with Vite for hot reloading

## 📦 Tech Stack

- **Node.js 18+**: JavaScript runtime
- **Express.js**: Web application framework
- **TypeScript**: Type-safe development
- **Zod**: Runtime type validation and schema definition
- **tsx**: TypeScript execution for development
- **Vite**: Development server integration

## 🚀 Getting Started

### Prerequisites
- Node.js 18 or higher
- npm or yarn package manager

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set environment variables**
   ```bash
   # Required for AI chatbot functionality
   export OPENAI_API_KEY="your-openai-api-key"
   
   # Optional environment variables
   export NODE_ENV="development"
   export PORT="5000"
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

The server will start on `http://localhost:5000` with hot reloading enabled.

## 📁 Project Structure

```
server/
├── index.ts          # Application entry point and server setup
├── routes.ts         # API route definitions and handlers
├── storage.ts        # Data storage abstraction layer
├── vite.ts          # Vite development server integration
└── README.md        # This file
```

## 🔧 Core Components

### 1. Server Setup (`index.ts`)
- Express application configuration
- Middleware setup (CORS, JSON parsing, sessions)
- Error handling middleware
- Server initialization and port binding

```typescript
const app = express();
const server = createServer(app);

// Middleware setup
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});
```

### 2. API Routes (`routes.ts`)
RESTful endpoints for application functionality:

#### Authentication Routes
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

#### Product Routes
- `GET /api/products` - Get all products with filtering
- `GET /api/products/:id` - Get specific product
- `POST /api/products` - Create new product (admin)
- `PUT /api/products/:id` - Update product (admin)
- `DELETE /api/products/:id` - Delete product (admin)

#### User Routes
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

### 3. Storage Layer (`storage.ts`)
Abstracted data storage with interface-based design:

```typescript
export interface IStorage {
  // User management
  getUser(id: number): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: Omit<User, 'id'>): Promise<User>;
  
  // Product management
  getProducts(): Promise<Product[]>;
  getProduct(id: number): Promise<Product | undefined>;
  createProduct(product: Omit<Product, 'id'>): Promise<Product>;
  updateProduct(id: number, updates: Partial<Product>): Promise<Product>;
  deleteProduct(id: number): Promise<boolean>;
}
```

#### In-Memory Implementation
Current implementation uses `Map` for fast data access:

```typescript
export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private products: Map<number, Product>;
  
  // Implementation details...
}
```

### 4. Development Integration (`vite.ts`)
Seamless integration with Vite for development:
- Hot module reloading
- Frontend/backend on same port
- Static file serving
- Development middleware

## 🔒 Authentication

The backend implements session-based authentication:

### Session Management
```typescript
app.use(session({
  secret: process.env.SESSION_SECRET || 'development-secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));
```

### Login Process
1. Client sends email/password to `/api/auth/login`
2. Server validates credentials against storage
3. Creates session and returns user data
4. Subsequent requests include session cookie

### Protected Routes
```typescript
function requireAuth(req: Request, res: Response, next: NextFunction) {
  if (!req.session?.userId) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  next();
}
```

## 📊 Data Models

### User Schema
```typescript
export const userSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  name: z.string(),
});
```

### Product Schema
```typescript
export const productSchema = z.object({
  id: z.number(),
  title: z.string(),
  brand: z.string(),
  price: z.number(),
  autoshipPrice: z.number(),
  rating: z.number().min(0).max(5),
  reviewCount: z.number(),
  image: z.string(),
  images: z.array(z.string()),
  deal: z.boolean(),
  flavors: z.array(z.string()),
  sizes: z.array(z.object({
    name: z.string(),
    price: z.number(),
    pricePerLb: z.string(),
  })),
  description: z.string(),
  inStock: z.boolean(),
  category: z.string(),
  keywords: z.array(z.string()),
});
```

## 🔍 API Reference

### Authentication Endpoints

#### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "message": "Login successful"
}
```

#### GET /api/auth/me
Get current authenticated user.

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Product Endpoints

#### GET /api/products
Get all products with optional filtering.

**Query Parameters:**
- `category` - Filter by product category
- `brand` - Filter by brand name
- `minPrice` - Minimum price filter
- `maxPrice` - Maximum price filter
- `search` - Search in title and keywords
- `sort` - Sort by: `price`, `rating`, `title`
- `order` - Sort order: `asc`, `desc`

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "title": "Premium Dog Food",
      "brand": "Merrick",
      "price": 45.99,
      "autoshipPrice": 41.39,
      "rating": 4.5,
      "reviewCount": 1200,
      // ... other fields
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

#### GET /api/products/:id
Get specific product by ID.

**Response:**
```json
{
  "product": {
    "id": 1,
    "title": "Premium Dog Food",
    // ... full product details
  }
}
```

## 🛠 Development Features

### Hot Reloading
The server automatically restarts when files change:
```bash
# Development with hot reloading
npm run dev
```

### Type Safety
Full TypeScript implementation with strict type checking:
```typescript
// Type-safe request handlers
app.get('/api/products/:id', async (req: Request, res: Response) => {
  const productId = parseInt(req.params.id);
  const product = await storage.getProduct(productId);
  
  if (!product) {
    return res.status(404).json({ error: 'Product not found' });
  }
  
  res.json({ product });
});
```

### Input Validation
Zod schemas ensure data integrity:
```typescript
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = loginSchema.parse(req.body);
    // Process login...
  } catch (error) {
    return res.status(400).json({ error: 'Invalid input' });
  }
});
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `development` |
| `PORT` | Server port | `5000` |
| `OPENAI_API_KEY` | OpenAI API key for chatbot | Required |
| `SESSION_SECRET` | Session encryption secret | `development-secret` |

### Production Configuration
```bash
# Production environment
export NODE_ENV=production
export PORT=3000
export SESSION_SECRET=your-secure-secret
export OPENAI_API_KEY=your-openai-key
```

## 📈 Performance Considerations

### In-Memory Storage
Current implementation uses in-memory storage for demo purposes:
- **Pros**: Fast access, no external dependencies
- **Cons**: Data lost on restart, not scalable
- **Production**: Replace with database (PostgreSQL, MongoDB, etc.)

### Caching Strategy
Consider implementing caching for production:
```typescript
// Redis caching example
const redis = require('redis');
const client = redis.createClient();

async function getCachedProducts() {
  const cached = await client.get('products');
  if (cached) return JSON.parse(cached);
  
  const products = await storage.getProducts();
  await client.setex('products', 300, JSON.stringify(products));
  return products;
}
```

## 🔐 Security

### Best Practices Implemented
- **Input Validation**: Zod schema validation
- **Session Security**: HTTP-only cookies, secure in production
- **CORS Configuration**: Proper origin handling
- **Error Handling**: No sensitive data in error responses

### Production Security Checklist
- [ ] Use HTTPS in production
- [ ] Set strong session secrets
- [ ] Implement rate limiting
- [ ] Add request size limits
- [ ] Use helmet.js for security headers
- [ ] Implement proper logging

## 🚀 Deployment

### Local Production Build
```bash
# Build the application
npm run build

# Start production server
npm start
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 5000
CMD ["npm", "start"]
```

### Environment Setup
```bash
# Production environment variables
NODE_ENV=production
PORT=3000
SESSION_SECRET=your-secure-random-string
OPENAI_API_KEY=your-openai-api-key
```

## 🧪 Testing

### Manual Testing
```bash
# Test authentication
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Test products endpoint
curl http://localhost:5000/api/products

# Test specific product
curl http://localhost:5000/api/products/1
```

### API Testing Tools
- **Postman**: GUI for API testing
- **curl**: Command-line testing
- **Thunder Client**: VS Code extension

## 🔄 Database Migration

To migrate from in-memory to persistent storage:

1. **Choose Database**: PostgreSQL, MySQL, MongoDB
2. **Update Storage Interface**: Keep same interface, change implementation
3. **Add Migration Scripts**: Database schema creation
4. **Update Configuration**: Database connection settings

Example PostgreSQL migration:
```typescript
import { Pool } from 'pg';

export class PostgresStorage implements IStorage {
  private pool: Pool;
  
  constructor() {
    this.pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });
  }
  
  async getUser(id: number): Promise<User | undefined> {
    const result = await this.pool.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return result.rows[0];
  }
  
  // ... other methods
}
```

## 📝 Logging

Add comprehensive logging for production:
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Use in route handlers
app.post('/api/auth/login', async (req, res) => {
  logger.info('Login attempt', { email: req.body.email });
  // ... login logic
});
```

## 🤝 Contributing

1. Follow TypeScript best practices
2. Add proper error handling
3. Include input validation
4. Update API documentation
5. Add tests for new features

## 📞 Support

For backend-specific issues:
- Check server logs for errors
- Verify environment variables
- Test API endpoints individually
- Review database connections (if applicable)

---

Built with 🛡️ for secure and scalable pet shopping experiences