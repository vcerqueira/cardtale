# Cardtale project

wip

## Intro

Exploratory data analysis is a fundamental stage in the life-cycle of data science projects. Importing, analysing, and preparing the data takes most of the time in these projects. So, it is desirable to come up with strategies that make this process more efficient.

The goal of this project is to partially automate the exploratory data analysis stage. To build a set of graphical analyses and respective interpretation based on an input data set.

The objective is not to replace the work of a data analyst, or the input of a domain expert. Rather, the tool is designed to speed up knowledge extraction from the data set. It guides the analyst towards more promising directions for a better data exploration without impeding the creative input from analysts.

Data types:
- Univariate time series
- Monthly data for now, to be expanded to other granularities, and then to multivariate time series


## Structure

For a given input time series, the initial sub-goal is to make a visual description of the data.
The extension of the analysis depends on the results of statistical tests and landmark experiments.

### Basic Structural Analysis (Fixed, Always presented)

In this part, the basic structure of the time series is presented to the reader.
Includes:
- Time series plot
    - Simple
    - and smoothed by higher granularities
- Distribution analysis
    - Histogram
    - Boxplot
- Decomposition analysis
    - Trend + seasonality
- Auto-correlation analysis
    - Complete and partial plots


### Trend Analysis (Shown if tests suggest a strong trend)

In this part, we make several tests which verify whether there’s a strong trend component in the series. If so, a few plots are created to illustrate this component.

Tests include:
- Effect of t as a feature in forecasting performance
- Effect of differencing in forecasting performance
- Stationarity tests (ndiffs)
- Correlation on t

Plots includes:
- ...

### Seasonality Analysis (Shown if tests suggest a strong seasonality, for different periods)

Similar to the trend, but for seasonality.
But, there’s an important detail. Seasonality can have multiple periods.
So, this analysis is carried out for each plausible period.

Tests include:
- Effect of Seasonal differencing in forecasting performance
- Effect of Fourier terms in forecasting performance
- Effect of RBF terms in forecasting performance
- nsdiffs test
- kats acf test

Plots include:
- Seasonal plots
- Tiles (period 1 vs period 2)
- Stacked Boxplot by period, color by higher period
- Ridge plots

### Variance Analysis (Shown if tests suggest a non-constant variance)

This component analysis whether there’s a non-constant variance in the series.

Tests include:
- White test
- Breusch-Pagan test
- breakvar_heteroskedasticity_test 
- Effect of log in forecasting performance
- Effect of box-cox in forecasting performance

Plots include:
- Partial violin plot (before-after)
- Line plot rolling std


### Change Analysis (Shown if tests find any change point)

This component involves detecting change points in univariate time series

Tests include (all from kats):
- Robust
- CUSUM
- Bayesian

Plots include:
- Lineplot + change points
- Partial violin (before/after)
- Density plot (before/after)


## Code Overview

- **__development** directory:
  1. a set of development scripts
- **base** package:
  1. class for univariate time series (uvts)
  2. class for handling frequency sets 
- **charts** package:
  1. A set of charts based on plotnine
- **components** package:
  1. classes for handling the different components of analysis
- **config** package:
  1. configurations
- **landmarks** package:
  1. package for running experiments
- **preprocess** package:
  1. set of preprocessing steps for time series
- **reporting** package:
  1. building the text analysis of the series and building the report
- **strings** package:
  1. jinja2 templates
- **templates** directory:
  1. html template
- **tsa** package:
  1. package for time series analysis











