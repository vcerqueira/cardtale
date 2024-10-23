from typing import List, Union

from scipy.stats import f_oneway, kruskal
from scipy.stats import levene, bartlett


class GroupMoments:

    @staticmethod
    def anova_test(group_list: List[Union[float, int]]):
        """Equal means"""
        stat, p_value = f_oneway(*group_list)

        return p_value

    @staticmethod
    def kruskal_test(group_list: List[Union[float, int]]):
        """Equal medians, non-parametric"""
        stat, p_value = kruskal(*group_list)

        return p_value

    @staticmethod
    def levene_test(group_list: List[Union[float, int]]):
        """Equal vars -> Not Normal, more robust"""
        stat, p_value = levene(*group_list)

        return p_value

    @staticmethod
    def bartlett_test(group_list: List[Union[float, int]]):
        """Equal vars -> Normal"""
        stat, p_value = bartlett(*group_list)

        return p_value

    @classmethod
    def compare_groups(cls, group_list: List):
        comparisons = {
            'eq_means': cls.anova_test(group_list),
            'eq_medians': cls.kruskal_test(group_list),
            'eq_std': cls.levene_test(group_list),
            'eq_std_normal': cls.bartlett_test(group_list),
        }

        return comparisons
