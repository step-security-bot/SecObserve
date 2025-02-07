from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    Index,
    IntegerField,
    ManyToManyField,
    Model,
    TextField,
)
from django.utils import timezone

from application.access_control.models import User
from application.core.services.observation import (
    get_identity_hash,
    normalize_observation_fields,
)
from application.core.types import Severity, Status
from application.import_observations.types import Parser_Source, Parser_Type
from application.issue_tracker.types import Issue_Tracker


class Product(Model):
    name = CharField(max_length=255, unique=True)
    description = TextField(max_length=2048, blank=True)

    is_product_group = BooleanField(default=False)
    product_group = ForeignKey(
        "self", on_delete=PROTECT, related_name="products", null=True, blank=True
    )

    repository_prefix = CharField(max_length=255, blank=True)
    repository_default_branch = ForeignKey(
        "Branch",
        on_delete=SET_NULL,
        related_name="repository_default_branch",
        null=True,
    )
    repository_branch_housekeeping_active = BooleanField(null=True)
    repository_branch_housekeeping_keep_inactive_days = IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(999999)]
    )
    repository_branch_housekeeping_exempt_branches = CharField(
        max_length=255, blank=True
    )

    security_gate_passed = BooleanField(null=True)
    security_gate_active = BooleanField(null=True)
    security_gate_threshold_critical = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    security_gate_threshold_high = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    security_gate_threshold_medium = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    security_gate_threshold_low = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    security_gate_threshold_none = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    security_gate_threshold_unkown = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )

    members: ManyToManyField = ManyToManyField(
        User, through="Product_Member", related_name="product_members", blank=True
    )
    apply_general_rules = BooleanField(default=True)

    notification_ms_teams_webhook = CharField(max_length=255, blank=True)
    notification_slack_webhook = CharField(max_length=255, blank=True)
    notification_email_to = CharField(max_length=255, blank=True)

    issue_tracker_active = BooleanField(default=False)
    issue_tracker_type = CharField(
        max_length=12, choices=Issue_Tracker.ISSUE_TRACKER_TYPE_CHOICES, blank=True
    )
    issue_tracker_base_url = CharField(max_length=255, blank=True)
    issue_tracker_username = CharField(max_length=255, blank=True)
    issue_tracker_api_key = CharField(max_length=255, blank=True)
    issue_tracker_project_id = CharField(max_length=255, blank=True)
    issue_tracker_labels = CharField(max_length=255, blank=True)
    issue_tracker_issue_type = CharField(max_length=255, blank=True)
    issue_tracker_status_closed = CharField(max_length=255, blank=True)
    issue_tracker_minimum_severity = CharField(
        max_length=12, choices=Severity.SEVERITY_CHOICES, blank=True
    )

    last_observation_change = DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    @property
    def open_critical_observation_count(self):
        if self.is_product_group:
            count = 0
            for product in Product.objects.filter(product_group=self):
                count += product.open_critical_observation_count
            return count

        return Observation.objects.filter(
            product=self,
            branch=self.repository_default_branch,
            current_status=Status.STATUS_OPEN,
            current_severity=Severity.SEVERITY_CRITICAL,
        ).count()

    @property
    def open_high_observation_count(self):
        if self.is_product_group:
            count = 0
            for product in Product.objects.filter(product_group=self):
                count += product.open_high_observation_count
            return count

        return Observation.objects.filter(
            product=self,
            branch=self.repository_default_branch,
            current_status=Status.STATUS_OPEN,
            current_severity=Severity.SEVERITY_HIGH,
        ).count()

    @property
    def open_medium_observation_count(self):
        if self.is_product_group:
            count = 0
            for product in Product.objects.filter(product_group=self):
                count += product.open_medium_observation_count
            return count

        return Observation.objects.filter(
            product=self,
            branch=self.repository_default_branch,
            current_status=Status.STATUS_OPEN,
            current_severity=Severity.SEVERITY_MEDIUM,
        ).count()

    @property
    def open_low_observation_count(self):
        if self.is_product_group:
            count = 0
            for product in Product.objects.filter(product_group=self):
                count += product.open_low_observation_count
            return count

        return Observation.objects.filter(
            product=self,
            branch=self.repository_default_branch,
            current_status=Status.STATUS_OPEN,
            current_severity=Severity.SEVERITY_LOW,
        ).count()

    @property
    def open_none_observation_count(self):
        if self.is_product_group:
            count = 0
            for product in Product.objects.filter(product_group=self):
                count += product.open_none_observation_count
            return count

        return Observation.objects.filter(
            product=self,
            branch=self.repository_default_branch,
            current_status=Status.STATUS_OPEN,
            current_severity=Severity.SEVERITY_NONE,
        ).count()

    @property
    def open_unkown_observation_count(self):
        if self.is_product_group:
            count = 0
            for product in Product.objects.filter(product_group=self):
                count += product.open_unkown_observation_count
            return count

        return Observation.objects.filter(
            product=self,
            branch=self.repository_default_branch,
            current_status=Status.STATUS_OPEN,
            current_severity=Severity.SEVERITY_UNKOWN,
        ).count()


class Branch(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    name = CharField(max_length=255)
    last_import = DateTimeField(null=True)
    housekeeping_protect = BooleanField(default=False)

    class Meta:
        unique_together = (
            "product",
            "name",
        )
        indexes = [
            Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    @property
    def open_critical_observation_count(self):
        return Observation.objects.filter(
            branch=self,
            current_severity=Severity.SEVERITY_CRITICAL,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_high_observation_count(self):
        return Observation.objects.filter(
            branch=self,
            current_severity=Severity.SEVERITY_HIGH,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_medium_observation_count(self):
        return Observation.objects.filter(
            branch=self,
            current_severity=Severity.SEVERITY_MEDIUM,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_low_observation_count(self):
        return Observation.objects.filter(
            branch=self,
            current_severity=Severity.SEVERITY_LOW,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_none_observation_count(self):
        return Observation.objects.filter(
            branch=self,
            current_severity=Severity.SEVERITY_NONE,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_unkown_observation_count(self):
        return Observation.objects.filter(
            branch=self,
            current_severity=Severity.SEVERITY_UNKOWN,
            current_status=Status.STATUS_OPEN,
        ).count()


class Service(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    name = CharField(max_length=255)

    class Meta:
        unique_together = (
            "product",
            "name",
        )
        indexes = [
            Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    @property
    def open_critical_observation_count(self):
        return Observation.objects.filter(
            origin_service=self,
            branch=self.product.repository_default_branch,
            current_severity=Severity.SEVERITY_CRITICAL,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_high_observation_count(self):
        return Observation.objects.filter(
            origin_service=self,
            branch=self.product.repository_default_branch,
            current_severity=Severity.SEVERITY_HIGH,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_medium_observation_count(self):
        return Observation.objects.filter(
            origin_service=self,
            branch=self.product.repository_default_branch,
            current_severity=Severity.SEVERITY_MEDIUM,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_low_observation_count(self):
        return Observation.objects.filter(
            origin_service=self,
            branch=self.product.repository_default_branch,
            current_severity=Severity.SEVERITY_LOW,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_none_observation_count(self):
        return Observation.objects.filter(
            origin_service=self,
            branch=self.product.repository_default_branch,
            current_severity=Severity.SEVERITY_NONE,
            current_status=Status.STATUS_OPEN,
        ).count()

    @property
    def open_unkown_observation_count(self):
        return Observation.objects.filter(
            origin_service=self,
            branch=self.product.repository_default_branch,
            current_severity=Severity.SEVERITY_UNKOWN,
            current_status=Status.STATUS_OPEN,
        ).count()


class Product_Member(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
    role = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = (
            "product",
            "user",
        )


class Parser(Model):
    name = CharField(max_length=255, unique=True)
    type = CharField(max_length=16, choices=Parser_Type.TYPE_CHOICES)
    source = CharField(max_length=16, choices=Parser_Source.SOURCE_CHOICES)

    class Meta:
        indexes = [
            Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Observation(Model):
    product = ForeignKey(Product, on_delete=PROTECT)
    branch = ForeignKey(Branch, on_delete=CASCADE, null=True)
    parser = ForeignKey(Parser, on_delete=PROTECT)
    title = CharField(max_length=255)
    description = TextField(max_length=2048, blank=True)
    recommendation = TextField(max_length=2048, blank=True)
    current_severity = CharField(max_length=12, choices=Severity.SEVERITY_CHOICES)
    numerical_severity = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    parser_severity = CharField(
        max_length=12, choices=Severity.SEVERITY_CHOICES, blank=True
    )
    rule_severity = CharField(
        max_length=12, choices=Severity.SEVERITY_CHOICES, blank=True
    )
    assessment_severity = CharField(
        max_length=12, choices=Severity.SEVERITY_CHOICES, blank=True
    )
    current_status = CharField(max_length=16, choices=Status.STATUS_CHOICES)
    parser_status = CharField(max_length=16, choices=Status.STATUS_CHOICES, blank=True)
    rule_status = CharField(max_length=16, choices=Status.STATUS_CHOICES, blank=True)
    assessment_status = CharField(
        max_length=16, choices=Status.STATUS_CHOICES, blank=True
    )
    scanner_observation_id = CharField(max_length=255, blank=True)
    vulnerability_id = CharField(max_length=255, blank=True)
    origin_component_name = CharField(max_length=255, blank=True)
    origin_component_version = CharField(max_length=255, blank=True)
    origin_component_name_version = CharField(max_length=513, blank=True)
    origin_component_purl = CharField(max_length=255, blank=True)
    origin_component_cpe = CharField(max_length=255, blank=True)
    origin_component_dependencies = TextField(max_length=2048, blank=True)
    origin_docker_image_name = CharField(max_length=255, blank=True)
    origin_docker_image_tag = CharField(max_length=255, blank=True)
    origin_docker_image_name_tag = CharField(max_length=513, blank=True)
    origin_docker_image_name_tag_short = CharField(max_length=513, blank=True)
    origin_docker_image_digest = CharField(max_length=255, blank=True)
    origin_endpoint_url = TextField(max_length=2048, blank=True)
    origin_endpoint_scheme = CharField(max_length=255, blank=True)
    origin_endpoint_hostname = CharField(max_length=255, blank=True)
    origin_endpoint_port = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(65535)]
    )
    origin_endpoint_path = TextField(max_length=2048, blank=True)
    origin_endpoint_params = TextField(max_length=2048, blank=True)
    origin_endpoint_query = TextField(max_length=2048, blank=True)
    origin_endpoint_fragment = TextField(max_length=2048, blank=True)
    origin_service_name = CharField(max_length=255, blank=True)
    origin_service = ForeignKey(Service, on_delete=PROTECT, null=True)
    origin_source_file = CharField(max_length=255, blank=True)
    origin_source_line_start = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    origin_source_line_end = IntegerField(
        null=True, validators=[MinValueValidator(0), MaxValueValidator(999999)]
    )
    origin_cloud_provider = CharField(max_length=255, blank=True)
    origin_cloud_account_subscription_project = CharField(max_length=255, blank=True)
    origin_cloud_resource = CharField(max_length=255, blank=True)
    origin_cloud_resource_type = CharField(max_length=255, blank=True)
    origin_cloud_qualified_resource = CharField(max_length=255, blank=True)
    cvss3_score = DecimalField(max_digits=3, decimal_places=1, null=True)
    cvss3_vector = CharField(max_length=255, blank=True)
    cwe = IntegerField(
        null=True, validators=[MinValueValidator(1), MaxValueValidator(999999)]
    )
    epss_score = DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    epss_percentile = DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    found = DateField(null=True)
    scanner = CharField(max_length=255, blank=True)
    upload_filename = CharField(max_length=255, blank=True)
    api_configuration_name = CharField(max_length=255, blank=True)
    import_last_seen = DateTimeField()
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    last_observation_log = DateTimeField(default=timezone.now)
    identity_hash = CharField(max_length=64)
    general_rule = ForeignKey(
        "rules.Rule",
        related_name="general_rules",
        blank=True,
        null=True,
        on_delete=PROTECT,
    )
    product_rule = ForeignKey(
        "rules.Rule",
        related_name="product_rules",
        blank=True,
        null=True,
        on_delete=PROTECT,
    )
    issue_tracker_issue_id = CharField(max_length=255, blank=True)
    issue_tracker_issue_closed = BooleanField(default=False)
    issue_tracker_jira_initial_status = CharField(max_length=255, blank=True)
    has_potential_duplicates = BooleanField(default=False)

    class Meta:
        indexes = [
            Index(fields=["product", "branch"]),
            Index(fields=["title"]),
            Index(fields=["current_severity"]),
            Index(fields=["numerical_severity"]),
            Index(fields=["current_status"]),
            Index(fields=["vulnerability_id"]),
            Index(fields=["origin_component_name_version"]),
            Index(fields=["origin_docker_image_name_tag_short"]),
            Index(fields=["origin_service_name"]),
            Index(fields=["origin_endpoint_hostname"]),
            Index(fields=["origin_source_file"]),
            Index(fields=["origin_cloud_qualified_resource"]),
            Index(fields=["last_observation_log"]),
            Index(fields=["epss_score"]),
            Index(fields=["scanner"]),
        ]

    def __str__(self):
        return f"{self.product} / {self.title}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.unsaved_references = []
        self.unsaved_evidences = []

    def save(self, *args, **kwargs) -> None:
        normalize_observation_fields(self)
        self.identity_hash = get_identity_hash(self)

        return super().save(*args, **kwargs)


class Observation_Log(Model):
    observation = ForeignKey(
        Observation, related_name="observation_logs", on_delete=CASCADE
    )
    user = ForeignKey(
        "access_control.User", related_name="observation_logs", on_delete=PROTECT
    )
    severity = CharField(max_length=12, choices=Severity.SEVERITY_CHOICES, blank=True)
    status = CharField(max_length=16, choices=Status.STATUS_CHOICES, blank=True)
    comment = CharField(max_length=255)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            Index(fields=["observation", "-created"]),
            Index(fields=["-created"]),
        ]
        ordering = ["observation", "-created"]


class Evidence(Model):
    observation = ForeignKey(Observation, related_name="evidences", on_delete=CASCADE)
    name = CharField(max_length=255)
    evidence = TextField()

    class Meta:
        indexes = [
            Index(fields=["name"]),
        ]


class Reference(Model):
    observation = ForeignKey(Observation, related_name="references", on_delete=CASCADE)
    url = TextField(max_length=2048)


class Potential_Duplicate(Model):
    POTENTIAL_DUPLICATE_TYPE_COMPONENT = "Component"
    POTENTIAL_DUPLICATE_TYPE_SOURCE = "Source"

    POTENTIAL_DUPLICATE_TYPES = [
        (POTENTIAL_DUPLICATE_TYPE_COMPONENT, POTENTIAL_DUPLICATE_TYPE_COMPONENT),
        (POTENTIAL_DUPLICATE_TYPE_SOURCE, POTENTIAL_DUPLICATE_TYPE_SOURCE),
    ]

    observation = ForeignKey(
        Observation, related_name="potential_duplicates", on_delete=CASCADE
    )
    potential_duplicate_observation = ForeignKey(Observation, on_delete=CASCADE)
    type = CharField(max_length=12, choices=POTENTIAL_DUPLICATE_TYPES)

    class Meta:
        unique_together = (
            "observation",
            "potential_duplicate_observation",
        )
