# UI/UX and Styling Guidelines for React Applications


To ensure a consistent, modern, and accessible user experience across all converted applications, follow these UI/UX and styling conventions, leveraging Material UI:


## Guidance

- **Design System:** Adopt a component-based design system, primarily using Material UI components. Leverage BC Design system and approach where possible and applicable.
- **Color Palette:** Utilize a defined color palette (e.g., BC Government or project-approved) for consistent branding and accessibility. Configure this palette in the Material UI theme.
- **Typography:** Use a readable, accessible font stack (e.g., `'BCSans', 'Noto Sans', Arial, sans-serif`) and apply it via the Material UI typography theme.
- **Spacing and Layout:** Use Material UI's built-in spacing helpers (`theme.spacing`) and responsive layout components (`Grid`, `Box`, `Stack`) for consistent padding, margins, and overall layout structure.
- **Component Theming:** Define a custom Material UI theme (`createTheme`) at the application root using `ThemeProvider`. Override default component styles (`components` section of the theme) to match the desired look and feel derived from Forms `VisualAttribute` and `PropertyClass` analysis.
- **Accessibility (WCAG 2.1+):**
  - Ensure sufficient color contrast for text and UI elements.
  - Use semantic HTML elements and ARIA attributes as provided or supported by Material UI.
  - Implement robust keyboard navigation and visible focus indicators.
  - Provide alternative text (`alt` attributes) for all meaningful images.
- **Error and Alert Handling:** Display user-friendly validation errors on form fields. Use Material UI `Alert`, `Snackbar`, or custom dialog components for displaying messages, warnings, and errors (`MESSAGE`, `ALERT` built-ins mapping).
- **Forms and Validation:** Use Material UI form components (`TextField`, `Select`, `Checkbox`, `RadioGroup`, `DatePicker`, etc.). Implement client-side validation for basic format/type checks. Clearly indicate required fields. Display server-side validation errors (returned from API calls triggered by `WHEN-VALIDATE-ITEM`, etc.) next to the relevant input field.
- **Branding:** Apply any necessary government or organizational branding elements (logos, headers, footers) as specified by project standards.
- **Icons:** Prefer using Material UI Icons or a project-approved icon set.
- **Responsive Design:** Design layouts to adapt to different screen sizes where appropriate, moving away from Forms' purely fixed-position layout.

## Reference Implementation
To see a practical example of these guidelines, refer to a starter React project demonstrating Material UI theming, layout, and component usage for a typical Forms screen structure. This project serves as a visual and structural reference for the generated code.

## BC Gov Design System Guidance (MANDATORY)

To ensure strict alignment with the [BC Government Design System](https://www2.gov.bc.ca/gov/content/digital/design-system), use the following official packages as the primary source of truth:

### 1. Mandatory Packages
- **React Components**: [`@bcgov/design-system-react-components`](https://www.npmjs.com/package/@bcgov/design-system-react-components)
  - *Usage*: Use these components (Header, Footer, Button, Input, etc.) **first**. Only fall back to Material UI if a specific component does not exist in this library.
  - *Ref*: [Component Library Documentation](https://www2.gov.bc.ca/gov/content/digital/design-system/components)

- **Typography**: [`@bcgov/bc-sans`](https://www.npmjs.com/package/@bcgov/bc-sans)
  - *Usage*: Must be installed and configured as the primary font family in the application theme/global CSS.

- **Design Token Variables**: [`@bcgov/design-tokens`](https://www.npmjs.com/package/@bcgov/design-tokens)
  - *Usage*: Use these CSS variables/tokens for all custom styling (colors, spacing, typography) to ensure brand consistency.

### 2. Implementation Strategy (Hybrid Approach)
1. **Primary**: Use `@bcgov/design-system-react-components` for all available UI elements.
2. **Secondary**: Use **Material UI (MUI)** for complex interactive components (Datagrids, complex date pickers) *not* covered by the BC library.
   - *Constraint*: You **MUST** theme the MUI components to exactly match the BC Gov visual style using `@bcgov/design-tokens`.
3. **Typography**: Ensure global application font is `BC Sans`.

### 3. Validation
- All generated components must be verified against the [Design System Standards](https://www2.gov.bc.ca/gov/content/digital/design-system).
- Visual QA must confirm that "Material UI fallbacks" are visually indistinguishable from native BC components.
