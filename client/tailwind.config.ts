import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)",
        },
        secondary: {
          DEFAULT: "var(--secondary)",
          foreground: "var(--secondary-foreground)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)",
        },
        destructive: {
          DEFAULT: "var(--destructive)",
          foreground: "var(--destructive-foreground)",
        },
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        chart: {
          "1": "var(--chart-1)",
          "2": "var(--chart-2)",
          "3": "var(--chart-3)",
          "4": "var(--chart-4)",
          "5": "var(--chart-5)",
        },
        sidebar: {
          DEFAULT: "var(--sidebar-background)",
          foreground: "var(--sidebar-foreground)",
          primary: "var(--sidebar-primary)",
          "primary-foreground": "var(--sidebar-primary-foreground)",
          accent: "var(--sidebar-accent)",
          "accent-foreground": "var(--sidebar-accent-foreground)",
          border: "var(--sidebar-border)",
          ring: "var(--sidebar-ring)",
        },
      },
      keyframes: {
        "accordion-down": {
          from: {
            height: "0",
          },
          to: {
            height: "var(--radix-accordion-content-height)",
          },
        },
        "accordion-up": {
          from: {
            height: "var(--radix-accordion-content-height)",
          },
          to: {
            height: "0",
          },
        },
        "fadeIn": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slideIn": {
          from: {
            transform: "translateY(-50px)",
            opacity: "0",
          },
          to: {
            transform: "translateY(0)",
            opacity: "1",
          },
        },
        "confettiFall": {
          "0%": {
            transform: "translateY(-50px) rotate(0deg)",
            opacity: "1",
          },
          "100%": {
            transform: "translateY(100vh) rotate(720deg)",
            opacity: "0",
          },
        },
        "bounce": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "vibrate": {
          "0%": { transform: "translateX(0) translateY(0) rotate(0deg)" },
          "10%": { transform: "translateX(-2px) translateY(-1px) rotate(-1deg)" },
          "20%": { transform: "translateX(2px) translateY(1px) rotate(1deg)" },
          "30%": { transform: "translateX(-2px) translateY(1px) rotate(-1deg)" },
          "40%": { transform: "translateX(2px) translateY(-1px) rotate(1deg)" },
          "50%": { transform: "translateX(-1px) translateY(2px) rotate(-0.5deg)" },
          "60%": { transform: "translateX(1px) translateY(-2px) rotate(0.5deg)" },
          "70%": { transform: "translateX(-2px) translateY(1px) rotate(-1deg)" },
          "80%": { transform: "translateX(2px) translateY(-1px) rotate(1deg)" },
          "90%": { transform: "translateX(-1px) translateY(2px) rotate(-0.5deg)" },
          "100%": { transform: "translateX(0) translateY(0) rotate(0deg)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fadeIn": "fadeIn 0.3s ease-in",
        "slideIn": "slideIn 0.3s ease-out",
        "confettiFall": "confettiFall 4s linear infinite",
        "bounce": "bounce 1s ease-in-out",
        "vibrate": "vibrate 0.1s linear infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate"), require("@tailwindcss/typography")],
} satisfies Config;
