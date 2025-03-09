# Reflection-milestone2

### **Implemented Features**

For Milestone 2, we developed a functional prototype of our `Green Gold: Unequal Gains` Dashboard. The dashboard integrates interactive visualizations that allow users to explore the relationship between avocado production and wage inequality in Michoacán. Key features include:
- Interactive Municipal Gini Map (Main Panel): Displays Gini coefficients by the municipality over time, with dropdowns to select the year and region type (Avocado Municipalities, Non-Avocado Municipalities, or Both).
- Summary Statistics (Top-Left Panel): Shows Gini coefficient trends for selected municipalities, highlighting key changes (e.g., pre- and post-2011 U.S. market access).
- Information Tables (Right-Side Panel): Toggle between two tables displaying statistical analyses:
    - Gini Regression Table (analyzing income inequality trends across municipalities).
    - Employment Regression Table (examining employment rate changes in avocado vs. non-avocado municipalities).
- Data Visualizations (Bottom Panel):
    - Production Trends: Line chart comparing avocado, corn, and blueberry production over time.
    - Income Inequality Trends: Time-series visualization of Gini coefficient changes across treatment and control groups.
    - Wage Distribution: Bar chart comparing wage levels between avocado and non-avocado regions.

### **Areas for Improvement and Limitation**
- General UI & Theme Improvements (Applies to All Sections):
    - Apply a light green colour scheme to maintain consistency with the `Green Gold` theme.
    - Improve readability and visibility by adjusting font style, size, spacing, and text contrast.
    - Optimize dashboard layout by expanding the width and adjusting element positioning to minimize scrolling and improve data presentation.
- Interactive Municipal Gini Map:
  -  Locate the Michoacán, Mexico area when displaying Gini coefficients in `both` mode.
- Information Tables (Right-Side Panel):
    - Improve table toggling visibility by highlighting the active selection and refining button styling (e.g., bold, active button, colour change) for a better user experience.
- Data Visualizations (Bottom Panel):
    - Gini Coefficients Graph: Add a vertical reference line for 2011 to indicate the policy change.
- Add operation instructions and explanations of terminology to improve the audience usage experience.
- Provide a `requirements.txt` file listing the necessary packages with specific versions to prevent compatibility issues and package-version conflicts.

### **Overall Reflection & Next Steps**
The `Green Gold: Unequal Gains` Dashboard presents an interactive and data-driven analysis of avocado production and wage inequality in Michoacán. Integrating maps, statistical summaries, and comparative charts provides an intuitive way for users to explore economic disparities over time. While the dashboard is fully functional, refining UI consistency, readability, and layout optimization will enhance the overall user experience. Moving forward, we will focus on styling improvements, interactive refinements, and ensuring an optimal layout before the final milestone.