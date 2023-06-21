from typing import Any, Dict, Iterable, List

from ._logger import logger
from ._map_synonyms import check_if_ids_in_field_values, map_synonyms


def inspect(
    df: Any,
    identifiers: Iterable,
    field: str,
    *,
    case_sensitive: bool = False,
    inspect_synonyms: bool = True,
    return_df: bool = False,
    logging: bool = True,
) -> Any:
    """Inspect if a list of identifiers are mappable to the entity reference.

    Args:
        identifiers: Identifiers that will be checked against the field.
        field: The BiontyField of the ontology to compare against.
                Examples are 'ontology_id' to map against the source ID
                or 'name' to map against the ontologies field names.
        case_sensitive: Whether the identifier inspection is case sensitive.
        inspect_synonyms: Whether to inspect synonyms.
        return_df: Whether to return a Pandas DataFrame.

    Returns:
        - A Dictionary of "mapped" and "unmapped" identifiers
        - If `return_df`: A DataFrame indexed by identifiers with a boolean `__mapped__`
            column that indicates compliance with the identifiers.
    """
    import pandas as pd

    # check if index is compliant
    mapped_df = check_if_ids_in_field_values(
        identifiers=identifiers,
        field_values=df[field],
        case_sensitive=case_sensitive,
    )

    def unique_rm_empty(idx: pd.Index):
        idx = idx.unique()
        return idx[(idx != "") & (~idx.isnull())]

    mapped = unique_rm_empty(mapped_df.index[mapped_df["__mapped__"]]).tolist()
    unmapped = unique_rm_empty(mapped_df.index[~mapped_df["__mapped__"]]).tolist()

    if inspect_synonyms:
        try:
            synonyms_mapper = map_synonyms(
                df=df,
                identifiers=unmapped,
                field=field,
                return_mapper=True,
                case_sensitive=case_sensitive,
            )
            if len(synonyms_mapper) > 0:
                logger.warning(
                    "The identifiers contain synonyms!\n   To increase mappability,"
                    " standardize them via '.map_synonyms()'"
                )
        except Exception:
            pass

    n_unique_terms = len(mapped) + len(unmapped)
    n_empty = len(list(identifiers)) - n_unique_terms
    frac_unmapped = round(len(unmapped) / n_unique_terms * 100, 1)
    frac_mapped = 100 - frac_unmapped

    if logging:
        if n_empty > 0:
            logger.warning(
                f"Received {n_unique_terms} unique terms, {n_empty} empty/duplicated"
                " terms are ignored."
            )
        logger.success(f"{len(mapped)} terms ({frac_mapped}%) are mapped.")
        logger.warning(f"{len(unmapped)} terms ({frac_unmapped}%) are not mapped.")

    if return_df:
        return mapped_df
    else:
        mapping: Dict[str, List[str]] = {}
        mapping["mapped"] = mapped
        mapping["not_mapped"] = unmapped
        return mapping
