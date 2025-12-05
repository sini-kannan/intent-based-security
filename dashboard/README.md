# Intent-Based Security Dashboard

A modern, responsive dashboard for monitoring and managing intent-based security policies across containerized applications. This dashboard provides real-time visibility into security drifts, policy enforcement, and compliance status.

![Dashboard Preview](https://via.placeholder.com/1200x600/1a237e/ffffff?text=Intent-Based+Security+Dashboard)

## Features

### Overview
- **Container Status** - At-a-glance view of all monitored containers
- **Security Score** - Overall security health indicator
- **Pipeline Status** - Visual representation of the security pipeline
- **Recent Alerts** - Quick view of recent security events

### Drift Analysis
- **Live Drift Detection** - Real-time identification of policy violations
- **Historical Trends** - Visualize security drifts over time
- **Detailed Reports** - In-depth analysis of each security incident
- **Container-Specific Views** - Filter drifts by container or service

### Enforcement Rules
- **Rule Management** - View and manage security rules
- **Policy Visualization** - Intuitive representation of iptables rules
- **Rule Testing** - Validate rules before enforcement
- **Audit Logs** - Track all rule changes and enforcements

### Quick Actions
- **Run Full Pipeline** - Execute the complete security pipeline
- **Export Reports** - Generate PDF reports of security status
- **Remediation** - One-click fixes for common security issues

## Getting Started

### Prerequisites
- Node.js 16+ and npm 8+
- Modern web browser (Chrome, Firefox, Safari, or Edge)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/intent-based-security.git
   cd intent-based-security/dashboard
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open in browser**
   The application will open automatically at [http://localhost:3000](http://localhost:3000)

## Development

### Available Scripts

- `npm start` - Start the development server
- `npm test` - Run tests
- `npm run build` - Create a production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
REACT_APP_API_URL=http://localhost:3001
REACT_APP_ENV=development
```

## Tech Stack

- **Frontend**: React 18, TypeScript, Material-UI 5
- **State Management**: React Context API
- **Routing**: React Router 6
- **Charts**: Recharts
- **Form Handling**: React Hook Form
- **Testing**: Jest, React Testing Library
- **Linting/Formatting**: ESLint, Prettier
