from typing import List, Union

from scipy.stats import f_oneway, kruskal
from scipy.stats import levene, bartlett

from cardtale.core.config.analysis import ALPHA


class GroupBasedTesting:
    """
    Class for performing group-based statistical tests on time series data.

    Methods:
        anova_test(group_list: List[Union[float, int]]) -> float:
            Performs ANOVA test to check for equal means.
        kruskal_test(group_list: List[Union[float, int]]) -> float:
            Performs Kruskal-Wallis test to check for equal medians (non-parametric).
        levene_test(group_list: List[Union[float, int]]) -> float:
            Performs Levene's test to check for equal variances (more robust, not assuming normality).
        bartlett_test(group_list: List[Union[float, int]]) -> float:
            Performs Bartlett's test to check for equal variances (assuming normality).
        run_tests(group_list: List) -> dict:
            Runs all group-based tests and returns a dictionary of p-values.
    """

    @staticmethod
    def anova_test(group_list: List[Union[float, int]]):
        """Equal means"""
        _, p_value = f_oneway(*group_list)

        means_are_eq = p_value > ALPHA

        return means_are_eq

    @staticmethod
    def kruskal_test(group_list: List[Union[float, int]]):
        """Equal medians, non-parametric"""
        _, p_value = kruskal(*group_list)

        medians_are_eq = p_value > ALPHA

        return medians_are_eq

    @staticmethod
    def levene_test(group_list: List[Union[float, int]]):
        """Equal vars -> Not Normal, more robust"""
        _, p_value = levene(*group_list)

        var_is_eq = p_value > ALPHA

        return var_is_eq

    @staticmethod
    def bartlett_test(group_list: List[Union[float, int]]):
        """Equal vars -> Normal"""
        _, p_value = bartlett(*group_list)

        varn_is_eq = p_value > ALPHA

        return varn_is_eq

    @classmethod
    def run_tests(cls, group_list: List):
        comparisons = {
            'means_are_eq': cls.anova_test(group_list),
            'medians_are_eq': cls.kruskal_test(group_list),
            'var_is_eq': cls.levene_test(group_list),
            'varn_is_eq': cls.bartlett_test(group_list),
        }

        return comparisons
