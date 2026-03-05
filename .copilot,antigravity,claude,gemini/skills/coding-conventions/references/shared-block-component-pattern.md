# Shared Block Component Pattern for Oracle Forms to React Conversion

## Purpose
This document provides guidance for efficiently converting Oracle Forms blocks to React components, maximizing code reuse and maintainability in the monorepo. It supplements existing documentation by detailing the shared block component pattern and when/how to use it.

## When to Use a Shared Block Component
- When multiple Oracle Forms blocks (e.g., code tables) share similar structure, layout, or logic.
- When converting forms like JUSE0005, which contain many blocks with nearly identical UI/data patterns.
- When you anticipate future forms will have similar requirements.

## How to Implement
1. **Create a Generic Block Component**
   - Place in `outputs/common/react/components/` (e.g., `FormBlock.tsx`).
   - Accept props for `title`, `children`, and optional layout/data props (e.g., scrollbars, record count).
   - Use Material-UI components for layout (e.g., `Paper`, `Box`, `Typography`).

2. **Use the Shared Component in Forms**
   - In your form (e.g., `JUSE0005Form.tsx`), replace repeated block layout code with the shared component.
   - Pass block-specific props and children as needed.

3. **Specialize Only When Needed**
   - If a block requires unique logic/UI, create a sub-component that composes the shared block.
   - Place sub-components in `common/react/components/` or a form-specific folder if truly unique.

4. **Centralize Types and Utilities**
   - Define shared types/interfaces in `common/react/types/` (e.g., `BlockProps`).
   - Move shared utilities (data fetching, validation) to `common/react/utils/`.

5. **Document Usage**
   - Add a comment or README in `common/react/components/` explaining the shared block’s intended usage and API.

## Example Usage
```tsx
// In outputs/common/react/components/FormBlock.tsx
import React from 'react';
import { Paper, Typography, Divider } from '@mui/material';

export interface FormBlockProps {
  title: string;
  children?: React.ReactNode;
}

const FormBlock: React.FC<FormBlockProps> = ({ title, children }) => (
  <Paper sx={{ p: 2, mb: 3 }}>
    <Typography variant="h6" gutterBottom>{title}</Typography>
    <Divider sx={{ mb: 2 }} />
    {children}
  </Paper>
);
export default FormBlock;
```

```tsx
// In outputs/common/react/forms/JUSE0005Form.tsx
import FormBlock from '../components/FormBlock';
// ...
{blocks.map((block) => (
  <FormBlock key={block} title={block.replace('JUSTIN_', '').replace('BLK', 'Block: ')}>
    {/* TODO: Render fields/items for {block} here */}
    <Typography variant="body2" color="text.secondary">
      [Fields for {block} will be generated here.]
    </Typography>
  </FormBlock>
))}
```

## Key Principles
- **Prefer composition and shared code.**
- **Only specialize when requirements diverge.**
- **Centralize types and utilities.**
- **Document new shared patterns.**

## When to Update This Guidance
- When new patterns emerge that benefit multiple forms/blocks.
- When the shared block component API changes.
- When you identify new best practices for Oracle Forms to React conversion.

---
_Last updated: 2025-05-24_
