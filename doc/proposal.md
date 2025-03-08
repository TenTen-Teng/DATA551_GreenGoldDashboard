## Motivation and Purpose  

**Our Role:** Data Science Research Team  
**Target Audience:** Government Officials, Policymakers, and Researchers  

In recent decades, Mexico has become the world's leading avocado exporter, with Michoacán at the center of this economic boom. The increased production and access to international markets, particularly the U.S., have generated significant economic growth. However, the effects of this expansion on local income distribution remain uncertain. While large agribusinesses and export companies have seen substantial profits, the impact on small farmers, laborers, and overall wage inequality is still unclear.  

To address this, we propose developing a data visualization dashboard that allows government officials, researchers, and policymakers to explore trends in avocado production and their potential connection to wage inequality in Michoacán. The dashboard will integrate municipal-level wage and production data, enabling users to analyze regional disparities, compare trends over time, and assess the potential socioeconomic effects of agricultural trade expansion. By providing interactive visualizations and data-driven insights, this tool will support more informed policy discussions on economic equity and rural development.

## Description of the Data  

For this project, we will use multiple datasets from official Mexican government sources, primarily focusing on agricultural production and labor market dynamics in Michoacán. These datasets will allow us to explore the relationship between avocado production and wage inequality at the municipal level.  

Our data comes from three main sources:  

1. **Agricultural Production Data (SIAP - agricultural_clean.csv)**  
   This dataset provides yearly agricultural production statistics, including the total production volume and production value of various crops. We will focus specifically on data related to Michoacán and extract the following variables:  
   - **year**: The year of production.  
   - **name_unitme_eng**: The crop name in English (e.g., "avocado").  
   - **production_volume**: The total amount of the crop produced (in tons).  
   - **production_value**: The total monetary value of the crop (in current Mexican pesos).  

2. **Employment Data (IMSS - Mexican Social Security Institute)**  
   We will use two tables from the IMSS database to examine employment trends and wage distribution across municipalities:  

   - **Economic Sector Employment (imss_economicsectors.csv)**: This table provides information on employment by economic sector in each municipality and year. We will use:  
     - **year**: The year of observation.  
     - **mun**: The municipality code.  
     - **trat**: A binary indicator of whether the municipality is an avocado-producing region.  
     - **pto**: A binary indicator marking pre- and post-expansion of avocado exports to the U.S. (2011).  
     - **se**: The economic sector classification.  
     - **value**: The number of registered jobs in each economic sector.  

   - **Wage Distribution Data (imss_minimumwages.csv)**: This table records wage levels for different municipalities and years, allowing us to assess income distribution. We will use:  
     - **year**: The year of observation.  
     - **mun**: The municipality code.  
     - **trat**: Whether the municipality is an avocado-producing region.  
     - **pto**: Pre- or post-2011 export expansion indicator.  
     - **q_minwages**: The wage category, expressed in multiples of the minimum wage (e.g., 3 times the minimum wage).  
     - **value**: The number of workers earning the corresponding wage level.  

3. **Income Inequality Data (Gini Coefficient - gini_mun_month_clean.csv)**  
   This dataset provides the core measure of inequality for our analysis. It contains:  
   - **year**: The year of measurement.  
   - **gini**: The calculated Gini coefficient for each municipality, which measures income inequality (higher values indicate greater inequality).  
   - **cve**: The municipality code (for mapping and spatial analysis).  
   - **mun_name**: The name of the municipality.  
   - **pto**: Pre- or post-2011 export expansion indicator.  
   - **trat_2**: Indicator of whether the municipality is an avocado-producing region.  
   - **date**: The specific month and year of the observation.  

### Data Exploration and Visualization Approach  
Our dashboard will integrate these datasets to explore:  
- Trends in avocado production and value over time.  
- Changes in employment and wage distribution across avocado-producing and non-producing municipalities.  
- Temporal and regional patterns in income inequality (Gini coefficient).  

By visualizing these data points, we aim to provide insights into how the expansion of avocado production correlates with employment, wages, and inequality, helping policymakers make informed decisions about economic development in Michoacán.  

## Research Questions  

The primary goal of our dashboard is to explore the relationship between avocado production and wage inequality in Michoacán. Given the rapid expansion of avocado exports and the associated economic changes, we seek to answer the following key research question:  

**"How has the growth in avocado production and exportation impacted wage distribution and income inequality in Michoacán’s municipalities?"**  

To provide a structured exploration, we break this down into the following sub-questions:  

1. **Production and Economic Growth:**  
   - How has avocado production volume and value evolved over time in Michoacán?  
   - Are there differences in production trends between municipalities?  

2. **Employment and Wages:**  
   - Has employment in avocado-producing municipalities grown at a different rate compared to non-producing municipalities?  
   - How has the wage distribution changed over time in municipalities that produce avocados versus those that do not?  
   - Are there shifts in the proportion of workers earning different multiples of the minimum wage in avocado-producing areas?  

3. **Income Inequality:**  
   - Has the Gini coefficient changed significantly in municipalities with high avocado production?  
   - Is there a noticeable trend in inequality before and after 2011, when full access to the U.S. market was granted?  
   - Do municipalities with larger avocado industries experience greater or lesser wage inequality compared to non-producing ones?  

### Target Audience & User Story  

Our primary target audience includes **government officials, policymakers, and researchers** focused on rural development, agricultural economics, and labor market dynamics. To better illustrate the potential use of our dashboard, we present a user persona and story:  

#### **Persona: María Rodríguez – Government Economist**  
**Background:** María is an economist working for Mexico’s Ministry of Agriculture. She is responsible for assessing the socioeconomic effects of agricultural policies and trade agreements. Her work involves analyzing how different economic sectors impact employment and income distribution in rural areas.  

#### **User Story:**  
María is preparing a report on the economic effects of the avocado boom in Michoacán. She has heard conflicting narratives, some claim that avocado production has brought prosperity, while others argue it has exacerbated inequality. She needs concrete data to support her analysis.  

Using the dashboard, María follows these steps:  

1. She **selects a time range** to compare economic trends before and after 2011, when the U.S. fully opened its market to Mexican avocados.  
2. She **filters by municipalities** to examine how avocado-producing and non-producing regions differ in employment growth and wage distribution.  
3. She **explores the Gini coefficient trends**, looking for patterns in inequality in avocado-producing areas.  
4. She **compares economic sectors**, checking if employment in agriculture has increased relative to other industries.  
5. She **downloads visualizations and insights** to include in her policy report.  

By the end of her session, María has gathered clear, data-driven insights that will help inform policy decisions regarding agricultural development and labor regulations in Mexico.  
