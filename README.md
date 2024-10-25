upcoming

# cardtale

Cardtale is a Python package for generating automated model and data cards, streamlining the documentation process for machine learning models and datasets.

## Introduction

In the machine learning lifecycle, proper documentation of models and datasets is crucial for transparency, reproducibility, and responsible AI practices. However, creating comprehensive model and data cards can be time-consuming. Cardtale aims to partially automate this process, making it more efficient and consistent.

The goal of Cardtale is to generate a set of analyses, visualizations, and interpretations based on input model metrics and dataset characteristics. While it doesn't replace the expertise of data scientists or domain experts, Cardtale speeds up the creation of model and data cards, guiding analysts towards key insights and areas that may require further exploration.

## Basic Example

```python
from datasetsforecast.m3 import M3

from cardtale.cards.builder import CardsBuilder

df, *_ = M3.load('./scripts', group='Monthly')

series = df.query('unique_id=="M1"').set_index('ds')['y']
series_df = df.query('unique_id=="M1"')

tcard = CardsBuilder(series_df, 'ME')
tcard.build_cards(render_html=True)
tcard.get_pdf()

```

## Installation

```
pip install cardtale
```


## License

Cardtale is released under the MIT License. See the [LICENSE](LICENSE) file for more details.