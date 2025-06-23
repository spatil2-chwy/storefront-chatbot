# Smart Pet Shopping Assistant - Chewy Style

A modern, AI-powered pet product shopping platform built with React, TypeScript, and Tailwind CSS, featuring an intelligent chatbot assistant that helps customers find the perfect products for their pets.

## 🚀 Features

### Frontend Features
- **Authentication System**: Secure login with email/password (dummy authentication for demo)
- **Product Browsing**: 
  - Grid-based product listing with filters
  - Advanced search functionality
  - Sort by price, rating, and relevance
  - Product categories and brand filtering
- **Product Details**: 
  - Detailed product pages with multiple images
  - Size and flavor selection
  - Autoship vs. Buy Once pricing options
  - Customer ratings and reviews display
- **AI Shopping Assistant**: 
  - Floating chatbot widget
  - Natural language product recommendations
  - Intelligent product filtering based on chat context
  - Real-time conversation with typing indicators
- **Responsive Design**: 
  - Mobile-first approach
  - Chewy brand-compliant styling
  - Modern UI components with shadcn/ui

### Backend Features
- **Express.js Server**: RESTful API architecture
- **In-Memory Storage**: Fast data access for demo purposes
- **User Management**: Authentication and user sessions
- **Product Management**: CRUD operations for products
- **Real-time Features**: WebSocket support for chat functionality

## 🛠 Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Wouter** - Lightweight routing
- **TanStack Query** - Server state management
- **shadcn/ui** - Modern UI components
- **Lucide React** - Beautiful icons

### Backend
- **Node.js** - JavaScript runtime
- **Express.js** - Web application framework
- **TypeScript** - Type-safe server development
- **Zod** - Schema validation
- **WebSocket** - Real-time communication

### Development Tools
- **Vite** - Fast build tool and dev server
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **PostCSS** - CSS processing

## 🎨 Design System

### Typography
- **Primary Font**: Poppins (headings, body text)
- **Secondary Font**: Work Sans (chat interface, secondary text)

### Colors
- **Primary Blue**: #004C98 (Chewy brand blue)
- **Accent Yellow**: #FFD100 (Chewy brand yellow)
- **Light Blue**: #E6F3FF (background accents)
- **Neutral Grays**: Various shades for text and backgrounds

### UI Components
- Rounded corners (rounded-xl, rounded-2xl)
- Subtle shadows and hover effects
- Card-based layout system
- Consistent spacing using Tailwind's scale

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pet-shopping-assistant
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Add your OpenAI API key for the chatbot feature
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run type checking
npm run type-check

# Lint code
npm run lint
```

## 🏗 Project Structure

```
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── ui/         # shadcn/ui components
│   │   │   ├── Header.tsx  # Navigation header
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductFilters.tsx
│   │   │   └── ChatWidget.tsx
│   │   ├── pages/          # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── ProductListing.tsx
│   │   │   └── ProductDetail.tsx
│   │   ├── lib/            # Utilities and hooks
│   │   │   ├── auth.tsx    # Authentication context
│   │   │   ├── mockData.ts # Sample product data
│   │   │   └── utils.ts    # Helper functions
│   │   ├── App.tsx         # Main application component
│   │   └── main.tsx        # Application entry point
│   └── index.html          # HTML template
├── server/                 # Backend Express application
│   ├── index.ts            # Server entry point
│   ├── routes.ts           # API routes
│   ├── storage.ts          # Data storage layer
│   └── vite.ts             # Vite development setup
├── shared/                 # Shared types and schemas
│   └── schema.ts           # Zod schemas and TypeScript types
└── README.md
```

## 🔐 Authentication

The application uses a simple authentication system for demonstration:

- **Login**: Any valid email and password combination will work
- **Session Management**: Authentication state is stored in localStorage
- **Protected Routes**: Product pages require authentication
- **Logout**: Click on the user name in the header to logout

## 🤖 AI Chatbot Features

The integrated chatbot provides intelligent shopping assistance:

### Capabilities
- **Natural Language Processing**: Understands pet care questions
- **Product Recommendations**: Suggests relevant products based on conversation
- **Smart Filtering**: Automatically filters products based on chat context
- **Contextual Responses**: Provides helpful information about pet care

### Example Interactions
- "How do I train my puppy to stop biting?" → Shows training treats and toys
- "I need grain-free dog food" → Filters to grain-free products
- "What's good for dental health?" → Shows dental chews and oral care products
- "My dog is a senior" → Recommends senior-specific formulas

### Technical Implementation
- OpenAI GPT-4 integration for intelligent responses
- Keyword extraction for product filtering
- Real-time chat interface with typing indicators
- Conversation history management

## 📱 Responsive Design

The application is fully responsive and works on:
- **Desktop**: Full-featured experience with sidebar filters
- **Tablet**: Adapted layout with collapsible navigation
- **Mobile**: Touch-optimized interface with mobile-first design

## 🔧 Customization

### Adding New Products
Edit `client/src/lib/mockData.ts` to add new products:

```typescript
export const mockProducts: Product[] = [
  {
    id: 1,
    title: "Product Name",
    brand: "Brand Name",
    price: 29.99,
    autoshipPrice: 26.99,
    rating: 4.5,
    reviewCount: 1200,
    // ... other properties
  },
  // Add more products
];
```

### Customizing Chat Responses
Modify the `generateAIResponse` function in `client/src/components/ChatWidget.tsx` to customize bot responses.

### Styling Changes
- Update colors in `client/src/index.css`
- Modify component styles using Tailwind classes
- Add custom CSS for advanced styling needs

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Environment Variables
Set these environment variables in production:
- `OPENAI_API_KEY`: Your OpenAI API key for chatbot functionality
- `NODE_ENV`: Set to "production"

### Hosting Recommendations
- **Frontend**: Vercel, Netlify, or any static hosting service
- **Backend**: Railway, Heroku, or any Node.js hosting platform
- **Full-Stack**: Replit, DigitalOcean App Platform

## 🧪 Testing

### Manual Testing Scenarios

1. **User Authentication**
   - Test login with various email formats
   - Verify logout functionality
   - Check protected route access

2. **Product Browsing**
   - Search for different product types
   - Test filtering by brand, price, size
   - Verify sorting functionality

3. **Product Details**
   - Navigate to product detail pages
   - Test size and flavor selection
   - Verify pricing calculations

4. **Chatbot Interaction**
   - Ask pet care questions
   - Test product filtering through chat
   - Verify response relevance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the GitHub Issues page
- Review the documentation
- Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial release with core shopping and chat features
- **v1.1.0**: Enhanced UI with Chewy branding and improved chatbot
- **v1.2.0**: Added comprehensive product filtering and search

---

Built with ❤️ for pet lovers everywhere