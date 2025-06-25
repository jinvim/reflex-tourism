# Reflective Resilience Index (REFLEX) for US Domestic Tourism Sector

This repository contains the resilience index for the US domestic tourism sector. The index is calculated for 3,108 counties in the contiguous US, for the years between 2018 and 2023.

## Reference

Please cite this work as:

Lee, S., & Pennington-Gray, L. (2025). Measuring Resilience of the Tourism Sector: Reflective Resilience Index (REFLEX) Approach, *Annals of Tourism Research, 114,* 103983. https://doi.org/10.1016/j.annals.2025.103983

- [Link to preprint](https://osf.io/984nr)
- [Link to dataset used in the study](https://osf.io/hz47m/)

## Overview of repository

- **data/**: folder containing the current and previous versions of the index
	- I plan to regularly update it whenever new data becomes available or methods have been updated.
- **scripts/**: folder containing Python code to process data and compute the index.
	- **reflex.py**: script that computes the index
	- **preprocess.py**: script that processes the original ADVAN data for computing the index.
		- Non-tourism visits (e.g., visits to workplace and home) are excluded during this stage
	- **utils.py**: collection of helper functions for computing the index

## Methods

### Rationale

Reflective Resilience Index (REFLEX) approach proposes that **diversified** and **balanced** demand are **reflective** indicators of tourism sector resilience.

- **diversified demand** regards availability of alternative demand segments
- **balanced demand** regards equal significance of each segment to the total demand.

We proposed that two characteristics are **reflective** indicators of tourism sector resilience because these are **outcomes** of the sector's capabilities.

### Operationalization

In the current version, we use the following operational definitions:

- **tourism sector** and **demand segment** are defined based on county boundary (i.e., destinations and origins).
- **demand** is measured based on the number of visits.

### Computing the index

In the current version, we use Shannon entropy to calculate the index:

$- \sum^{n}_{i} p_i \cdot ln(p_i)$

where $p_i$ is a proportion of the segment $i$'s contribution to the total demand, for available demand segments $i, \dots, n$.

- **diversification**: when the contributions to demand are equal among the segments, the score increases as the number of available segments increases ($n$)
- **balancing**: with a given number of demand sources ($n$), the score is maximized when each segment contributes equally ($p_i = 1/n$).

The score is calculated based on yearly visitation numbers.

### Data

The US mobility data used in this study were made available by ADVAN Research (https://advanresearch.com) via the Dewey Data platform (https://www.deweydata.io/).

## Additional notes

Our approach can be customized based on your purpose and data. For instance, one could define the tourism sector based on city boundaries and measure demand based on tourist spending. It is also possible to compute the index based on 

Although, **CAUTION that** scores obtained using different methods or data are not directly comparable.

## Change logs

- **v1.0** [2025-05-20]: Initial release

## Contact

If you have any questions or requests, feel free to reach out to me! Contacts are available in my profile.
