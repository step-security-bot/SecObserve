from typing import Optional

from django.db.models import Exists, OuterRef, Q
from django.db.models.query import QuerySet

from application.commons.services.global_request import get_current_user
from application.core.models import (
    Branch,
    Evidence,
    Observation,
    Potential_Duplicate,
    Product,
    Product_Member,
)


def get_observation_by_id(observation_id: int) -> Optional[Observation]:
    try:
        return Observation.objects.get(id=observation_id)
    except Observation.DoesNotExist:
        return None


def get_observations() -> QuerySet[Observation]:
    user = get_current_user()

    if user is None:
        return Observation.objects.none()

    observations = Observation.objects.all()

    if not user.is_superuser:
        product_members = Product_Member.objects.filter(
            product=OuterRef("product_id"), user=user
        )
        product_group_members = Product_Member.objects.filter(
            product=OuterRef("product__product_group"), user=user
        )

        observations = observations.annotate(
            product__member=Exists(product_members),
            product__product_group__member=Exists(product_group_members),
        )

        observations = observations.filter(
            Q(product__member=True) | Q(product__product_group__member=True)
        )

    return observations


def get_observations_for_vulnerability_check(
    product: Product,
    branch: Optional[Branch],
    filename: str,
    api_configuration_name: str,
) -> QuerySet[Observation]:
    return Observation.objects.filter(
        product=product,
        branch=branch,
        upload_filename=filename,
        api_configuration_name=api_configuration_name,
    )


def get_evidences() -> QuerySet[Evidence]:
    user = get_current_user()

    if user is None:
        return Evidence.objects.none()

    evidences = Evidence.objects.all()

    if not user.is_superuser:
        product_members = Product_Member.objects.filter(
            product=OuterRef("observation__product_id"), user=user
        )
        product_group_members = Product_Member.objects.filter(
            product=OuterRef("observation__product__product_group"), user=user
        )

        evidences = evidences.annotate(
            observation__product__member=Exists(product_members),
            observation__product__product_group__member=Exists(product_group_members),
        )

        evidences = evidences.filter(
            Q(observation__product__member=True)
            | Q(observation__product__product_group__member=True)
        )

    return evidences


def get_potential_duplicates() -> QuerySet[Potential_Duplicate]:
    user = get_current_user()

    if user is None:
        return Potential_Duplicate.objects.none()

    potential_duplicates = Potential_Duplicate.objects.all()

    if not user.is_superuser:
        product_members = Product_Member.objects.filter(
            product=OuterRef("observation__product_id"), user=user
        )
        product_group_members = Product_Member.objects.filter(
            product=OuterRef("observation__product__product_group"), user=user
        )

        potential_duplicates = potential_duplicates.annotate(
            observation__product__member=Exists(product_members),
            observation__product__product_group__member=Exists(product_group_members),
        )

        potential_duplicates = potential_duplicates.filter(
            Q(observation__product__member=True)
            | Q(observation__product__product_group__member=True)
        )

    return potential_duplicates
