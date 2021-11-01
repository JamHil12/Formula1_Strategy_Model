<div id="top"></div>

[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/JamHil12/Formula1_Strategy_Model">
    <img src="docs/images/logo.png" alt="Logo" width="306" height="114">
  </a>

<h3 align="center">Formula1_Strategy_Model</h3>

  <p align="center">
    Race strategy optimisation and visualisation tools, built on publicly available Formula One timing data.
    <br />
    <a href="https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/JamHil12/Formula1_Strategy_Model">View Demo</a>
    ·
    <a href="https://github.com/JamHil12/Formula1_Strategy_Model/issues">Report Bug</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
	<li><a href="#key-concepts-used">Key Concepts Used</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://github.com/JamHil12/Formula1_Strategy_Model)

A set of software tools to visualise the optimal race strategy for a single car, including:
* How the optimal strategy varies according to changes in tyre degradation characteristics.
* How each tyre compound compared in their degradation characteristics for historical F1 races.

Note that the real-world optimisation of race strategy in F1 is much more complex, due to the interactions between competitors. A simplified approach is adopted here, with a focus on software development.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Python v3.7](https://www.python.org/)
* [Jupyter notebook](https://jupyter.org/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

You will need:

* Create a Google Cloud Platform (GCP) account and a new Google BigQuery project, which will store all the datasets used in the modelling.
  [https://console.cloud.google.com/getting-started](https://console.cloud.google.com/getting-started)

* Python 3.7.
  [https://www.python.org/downloads/](https://www.python.org/downloads/)

### Installation

1. Clone the repo:
   ```sh
   git clone https://github.com/JamHil12/Formula1_Strategy_Model.git
   ```
   
2. Create a new Python virtual environment, and install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

3. Create datasets in your new BigQuery project called *"Custom_Lookups"*, *"F1_Modelling_Raw"* and *"F1_Modelling_Combined"* (note the underscores and letter casing). These will store all the publicly available F1 timing data that you need.
 
4. Create a new service account which has access to your BigQuery project, and store the json file for the service account's credentials in the *"tools/credentials"* folder.
   [https://cloud.google.com/docs/authentication/getting-started](https://cloud.google.com/docs/authentication/getting-started)

5. To run Jupyter notebooks, type the following command into the terminal once the Python virtual environment is activated.
   ```sh
   jupyter notebook
   ```

For more information on how to update lookups, download timing data and run the strategy models, please refer to the [Documentation.](https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/docs)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

* Parametrise the tyre degradation rate, and the pace advantage between compounds. Perform a parameter sweep to visualise the decision boundary between different optimal strategy choices.
  
  [![Parameter Sweep Screen Shot][parameter-sweep-screenshot]](https://github.com/JamHil12/Formula1_Strategy_Model)
  
  In the screenshot above, parameters 'k' and 'd' control the degradation rate and pace advantage between compounds, respectively.

* Fit lap time degradation curves to historical F1 race timing data, including (but not limited to) a quadratic fit.

* Estimate the the fuel effect on lap time, independently of tyre wear.

For a full demonstration, please refer to the Jupyter notebooks in the [build](https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/build) folder.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- KEY CONCEPTS -->
## Key Concepts Used

* Vectorization: over 10x improvement in computational speed by replacing for loops with vectorized equivalents.

* Databases and Cloud Storage: for ease of storing and retrieving timing data at scale, using SQL queries to manipulate the data appropiately.


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Jamie Hilton - [LinkedIn](https://linkedin.com/in/jamie-hilton-464493104)

Project Link: [https://github.com/JamHil12/Formula1_Strategy_Model](https://github.com/JamHil12/Formula1_Strategy_Model)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Ergast API](http://ergast.com/mrd/)
* [README file design](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[license-shield]: https://img.shields.io/github/license/JamHil12/Formula1_Strategy_Model.svg?style=for-the-badge
[license-url]: https://github.com/JamHil12/Formula1_Strategy_Model/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/jamie-hilton-464493104
[product-screenshot]: docs/images/deg_curves_by_compound.png
[product-sweep-screenshot]: docs/images/parameter_sweep.png
