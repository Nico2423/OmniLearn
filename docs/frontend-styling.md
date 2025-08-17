# Frontend Styling Guide

## Tailwind CSS v4 + Shadcn UI Setup

This project uses **Tailwind CSS v4** with **Shadcn UI components**. This combination requires special configuration because Shadcn was designed for Tailwind v3.

## CSS Variable Configuration

### The Problem
Shadcn UI components use CSS custom properties like `bg-primary`, `text-primary-foreground`, etc. In Tailwind v3, these were configured in `tailwind.config.js`. In Tailwind v4, configuration is handled in CSS files, but Shadcn components expect specific variable names.

### The Solution
The `frontend/app/globals.css` file contains the required CSS variable mappings:

```css
:root {
  /* Define variables without --color- prefix */
  --background: #ffffff;
  --foreground: #0f172a;
  --primary: #1e40af;
  --primary-foreground: #ffffff;
  --secondary: #f1f5f9;
  --secondary-foreground: #0f172a;
  --muted: #f1f5f9;
  --muted-foreground: #64748b;
  --accent: #f1f5f9;
  --accent-foreground: #0f172a;
  --destructive: #ef4444;
  --destructive-foreground: #ffffff;
  --border: #e2e8f0;
  --input: #e2e8f0;
  --ring: #1e40af;
  --card: #ffffff;
  --card-foreground: #0f172a;
  --popover: #ffffff;
  --popover-foreground: #0f172a;
  --radius: 0.5rem;
}

@theme {
  /* Map to --color-* format that Shadcn expects */
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
}
```

## Using Shadcn Components

### Button Component
```tsx
import { Button } from './ui/button';

// Primary button (blue background)
<Button>Click me</Button>

// Outlined button
<Button variant="outline">Cancel</Button>

// Destructive button (red)
<Button variant="destructive">Delete</Button>

// Small button
<Button size="sm">Small</Button>
```

### Common Variants
- `default`: Primary blue button
- `outline`: Border with transparent background
- `secondary`: Light gray background
- `destructive`: Red background for dangerous actions
- `ghost`: No background, hover effects only
- `link`: Styled like a link

### Sizes
- `default`: Standard button size
- `sm`: Small button
- `lg`: Large button
- `icon`: Square button for icons

## Troubleshooting

### Buttons Appear Unstyled
If Shadcn buttons appear as plain text without styling:

1. **Check CSS imports**: Ensure `globals.css` is imported in `app/layout.tsx`
2. **Verify CSS variables**: All variables in the `@theme` block must be present
3. **Check Tailwind build**: Restart the development server after CSS changes
4. **Browser cache**: Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)

### Adding New Shadcn Components
When adding new Shadcn components that use additional CSS variables:

1. Add the base variable to `:root` (without `--color-` prefix)
2. Add the mapping in `@theme` block (with `--color-` prefix)
3. Restart the development server

## Color Customization

To change the color scheme, update the values in `:root`:

```css
:root {
  --primary: #10b981; /* Change primary color to green */
  --primary-foreground: #ffffff;
  /* ... other colors */
}
```

The `@theme` mappings will automatically apply the new colors to all Shadcn components.