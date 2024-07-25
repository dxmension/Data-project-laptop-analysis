# Data Project: Data Analysis to Streamlit Web Application

<center>
  <img src="https://i.pinimg.com/originals/e4/d3/95/e4d395849317f98f2a418c0e10182b0d.gif" style="width:50%;">
</center>

## Objective | User Story
The Marketing Lead of KZ Laptop Trader Company found that revenue of the business had decreased significantly in the first quarter of year. CEO of the company also started raising concerns about the sales deduction. They decided to hire Data Analyst (me) to handle the situation.
* What is the key factor affecting laptop price?
<p>To answer the question we need extract key information from **data** that could not be provided by the company due to the database access issues. </p>
<p>We accepted such a challenge!</p>
<p>The final request was stated as following: 
<ul>
<li>Provide key metrics affecting laptop prices (in .pptx or jupyter notebook wih code samples)</li>
<li>Create recomendational system to extract laptop models that could be potentially purchased</li>
</ul>
</p>

## Stages
* Data Collection
* Data Organization
* Data Analysis
* Development

### Tools
<table>
  <tr>
    <td>Stage Step</td>
    <td>Tech Stack</td>
  </tr>
  <tr>
    <td>Data Collection</td>
    <td>requests, beautifulSoup4, assyncio</td>
  </tr>
  <tr>
    <td>Data Organization</td>
    <td>Pandas, Numpy</td>
  </tr>
  <tr>
    <td>Data Analysis</td>
    <td>seaborn, Plotly, matplotlib, pandas</td>
  </tr>
  <tr>
    <td>Development</td>
    <td>Streamlit, plotly, OpenAI</td>
  </tr>
</table>

## Data Collection
Before development and Data Analysis step, we are in high demand for data.
<p>It means that we need to collect it and save somewhere</p>
<p>Nowadays there are tons of methods how to extract information, using API, online web crawlers, etc. But to showcase our skills to requesters, I wanted to approach the problem using my exisiting knowledge in python packages enabling us to scrape data from websites</p>

#### BeautifulSoup
**Beautiful Soup** is a library that makes it easy to scrape information from web pages. It sits atop an HTML or XML parser, providing Pythonic idioms for iterating, searching, and modifying the parse tree.
<p>As a main website from where we will extract data is KZ Electronics Shop ("Belyi Veter").</p>
<p>To perform web scrapping, we need to 
<ul>
  <li>Make HTTP requests on URL</li>
  <li>Get inner HTML content</li>
  <li>Parse through the content tree to extract required information</li>
</ul>
<p>In more programmatical language, we made following steps:
  
**Setting Up Configuration**:

* Configures the logging format and level.
* Defines custom headers to mimic human interaction with the website and avoid being blocked.
  
  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5264826213891955301.jpg)
  
**Defining Asynchronous Function**
* request_with_retries(url, headers, session, retries=10)
    Makes HTTP requests with retries and exponential backoff to handle CAPTCHA and network issues.

  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5262702996809178717.jpg)
    
* parse_item_card(item)
    Parses an individual item card to extract laptop information such as ID, title, prices, specifications, and image link.

  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/9af03364-0272-44dc-8596-d6d86e1b1734.jpg)
  
* parse_listing(url, session)
    Parses the listing page to extract all item cards and their information. Returns a list of dictionaries containing laptop information and the BeautifulSoup object of the page.

  ![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5264826213891955329.jpg)

  
**Executing the Full Scraping Process**

Information was initially stored in JSON file, but I decided to switch to storing info in Python dictionaries and then convert them into pandas dataframes to speed up process of CSV saving.

#### The output of the Data Collection step is CSV document containing 3000+ laptop models with 21 column indicating feature of the product
</p>

## Data Organization
Data cleansing is a crucial process in data science that involves identifying and correcting (or removing) errors and inconsistencies in data to improve its quality. This process ensures that the dataset is accurate, complete, and reliable for analysis.

The general process looks as following:

**Data Inspection**:
* Uploading CSV file and inspect dataset thoroughly

![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5265003840854417965.jpg)

As the result of the inspection, total 2000+ datapoints were missing, no outliers and anomalies were found.

**Handling Missing Values**:

* Necessary datapoints were dropped, but mostly missing values were overwritten with central tendency measures of grouped laptops (grouping was based on the brand and CPU/GPU models)
    
The main and unsolved challenge is handling price feature: sometimes website owners do not update prices of products, and as a result scraper cannot collect info about it. Several methods were tried, but none of them could provide quality solution.
* Train regression model to predict missing prices on very small set of data entries (result: overfitting with trained data) - imbalancy between seen and unseen splits
* Overwrite NaNs with mode, median, or mean values for grouped laptops by brand name, cpu, gpu - outliers due to the imbalancy between splits as well
* Fill NaN with prompts to OpenAI API (most efficient, but unreliable in terms of data), so I decided to skip that step

#### The result of Data Organization and appropriate Feature Engineering is a cleaned dataset

![](https://github.com/dxmension/Data-project-laptop-analysis/blob/main/assets/5265003840854417978.jpg)



## Exploratory Data Analysis (EDA)
Exploratory Data Analysis (EDA) is a crucial step in the data analysis process. It involves summarizing the main characteristics of a dataset often using visual methods. EDA helps in understanding the data, uncovering patterns, spotting anomalies, testing hypotheses, and checking assumptions through statistical summaries and graphical representations. 

During EDA stage, some critical patterns and findings were identified using graphical and statistical methods:

* The most expensive brand is Apple, while the most popular brand is HP
* On average, gaming laptops are considerably higher in price than ordinary laptops due to the premium component
* The higher video standards, the higher price of laptops with the most expensive on UltraHD 4k+
* Basically, AMD is the best both GPU and CPU option from cost-performance perspective
* SSD and RAM configurations strongly affect price of a laptop with the highest Pearson correlation coefficient (~0.75)
* Operating system has no notable impact  on the laptop price, moreover, the picture becomes unclear, when DOS laptops cost higher than those of with OS
* Most laptops are equipped with NVIDIA with higher price, while mostly laptops use integrated graphics.

<a href="https://github.com/dxmension/Data-project-laptop-analysis/blob/main/scraper/project-2-laptop-configuration.ipynb">Jupyter Notebook</a> to see each stage in details
