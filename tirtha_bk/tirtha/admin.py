from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import ngettext

from .models import ARK, Contribution, Contributor, Image, Mesh, Run


class ContributionsInline(admin.TabularInline):
    def contribution_ts(self, obj):
        return obj.contributed_at

    contribution_ts.short_description = "Contribution Timestamp"

    def contribution_link(self, obj):
        url = reverse("admin:tirtha_contribution_change", args=[obj.ID])
        return mark_safe(f'<a href="{url}">{obj.ID}</a>')

    contribution_link.short_description = "Link to Contribution"

    model = Contribution
    readonly_fields = ("contribution_ts", "contribution_link", "processed")
    fields = ("ID", "contribution_ts", "contribution_link", "processed")
    extra = 0
    max_num = 0
    can_delete = True


class ContributionInlineMesh(ContributionsInline):
    def contributor_email(self, obj):
        return obj.contributor.email

    contributor_email.short_description = "Contributor Email"

    readonly_fields = ContributionsInline.readonly_fields + ("contributor_email",)
    fields = ContributionsInline.fields + ("contributor_email",)


class ContributionInlineContributor(ContributionsInline):
    def mesh_id(self, obj):
        return obj.mesh.verbose_id

    mesh_id.short_description = "Mesh ID (Verbose)"

    readonly_fields = ContributionsInline.readonly_fields + ("mesh_id",)
    fields = ContributionsInline.fields + ("mesh_id",)


class RunInlineMesh(admin.TabularInline):
    model = Run
    readonly_fields = ("ID", "ark", "status", "started_at", "ended_at")
    fields = ("ID", "ark", "status", "started_at", "ended_at")
    extra = 0
    max_num = 0
    can_delete = False


@admin.register(Mesh)
class MeshAdmin(admin.ModelAdmin):
    def get_preview(self, obj):
        return mark_safe(
            f'<img src="{obj.preview.url}" alt="{str(obj.verbose_id)}" style="width: 400px; height: 400px">'
        )

    get_preview.short_description = "Preview"

    def get_thumbnail(self, obj):
        return mark_safe(
            f'<img src="{obj.thumbnail.url}" alt="{str(obj.verbose_id)}" style="width: 400px; height: 400px">'
        )

    get_thumbnail.short_description = "Thumbnail"

    def mesh_id_verbose(self, obj):
        return obj.verbose_id

    mesh_id_verbose.short_description = "ID (Verbose)"

    def contrib_count(self, obj):
        return obj.contributions.count()

    contrib_count.short_description = "Contribution Count"

    def image_count(self, obj):
        return Image.objects.filter(contribution__mesh=obj).count()

    image_count.short_description = "Total Image Count"

    @admin.action(description="Mark selected meshes as completed")
    def mark_completed(self, request, queryset):
        updated = queryset.update(completed=True)
        self.message_user(
            request,
            ngettext(
                "%d mesh was successfully marked as completed.",
                "%d meshes were successfully marked as completed.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Mark selected meshes as incomplete")
    def mark_incomplete(self, request, queryset):
        updated = queryset.update(completed=False)
        self.message_user(
            request,
            ngettext(
                "%d mesh was successfully marked as incomplete.",
                "%d meshes were successfully marked as incomplete.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Mark selected meshes as hidden")
    def mark_hidden(self, request, queryset):
        updated = queryset.update(hidden=True)
        self.message_user(
            request,
            ngettext(
                "%d mesh was successfully marked as hidden.",
                "%d meshes were successfully marked as hidden.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Mark selected meshes as not hidden")
    def mark_not_hidden(self, request, queryset):
        updated = queryset.update(hidden=False)
        self.message_user(
            request,
            ngettext(
                "%d mesh was successfully marked as not hidden.",
                "%d meshes were successfully marked as not hidden.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    actions = [mark_completed, mark_incomplete, mark_hidden, mark_not_hidden]
    fieldsets = (
        (
            "Mesh Details",
            {
                "fields": (
                    ("ID", "verbose_id"),
                    ("created_at", "updated_at", "reconstructed_at"),
                    ("status", "completed", "hidden"),
                    ("name", "country", "state", "district"),
                    "description",
                    ("center_image", "denoise"),
                    (
                        "rotaZ",
                        "rotaX",
                        "rotaY",
                        "minObsAng",
                        "orientMesh",
                    ),  # Mimicking <model-viewer> attributes (ZXY)
                    ("thumbnail", "get_thumbnail"),
                    ("preview", "get_preview"),
                )
            },
        ),
    )
    readonly_fields = (
        "ID",
        "verbose_id",
        "created_at",
        "updated_at",
        "reconstructed_at",
        "get_preview",
        "get_thumbnail",
    )
    list_filter = (
        "status",
        "completed",
        "hidden",
    )
    list_display = (
        "ID",
        "mesh_id_verbose",
        "name",
        "reconstructed_at",
        "status",
        "completed",
        "hidden",
        "contrib_count",
        "image_count",
        "get_thumbnail",
    )
    list_per_page = 25
    inlines = [ContributionInlineMesh]  # , RunInlineMesh FIXME: Error while saving


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    def contrib_count(self, obj):
        return obj.contributions.count()

    contrib_count.short_description = "Contribution Count"

    def image_count(self, obj):
        return Image.objects.filter(contribution__contributor=obj).count()

    image_count.short_description = "Total Image Count"

    @admin.action(description="Ban selected contributors")
    def ban_contributors(self, request, queryset):
        updated = queryset.update(banned=True)
        self.message_user(
            request,
            ngettext(
                "%d contributor was successfully banned.",
                "%d contributors were successfully banned.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Unban selected contributors")
    def unban_contributors(self, request, queryset):
        updated = queryset.update(banned=False)
        self.message_user(
            request,
            ngettext(
                "%d contributor was successfully unbanned.",
                "%d contributors were successfully unbanned.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    actions = [ban_contributors, unban_contributors]
    readonly_fields = (
        "ID",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Contributor Details",
            {
                "fields": (
                    "ID",
                    ("created_at", "updated_at"),
                    ("name", "email"),
                    "banned",
                    "ban_reason",
                )
            },
        ),
    )
    inlines = [ContributionInlineContributor]
    list_filter = ("banned",)
    list_display = (
        "ID",
        "name",
        "email",
        "updated_at",
        "contrib_count",
        "image_count",
        "banned",
    )
    list_per_page = 50


class ImageInlineContribution(admin.TabularInline):
    """
    Shows images in the Contribution admin page

    """

    def get_image(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" style="width: 400px; height: 400px">'
        )

    get_image.short_description = "Preview"

    def image_link(self, obj):
        url = reverse("admin:tirtha_image_change", args=[obj.ID])
        return mark_safe(f'<a href="{url}">{obj.ID}</a>')

    image_link.short_description = "Link to Image"

    model = Image
    readonly_fields = ("get_image", "image_link")
    fields = (
        "ID",
        "get_image",
        "image_link",
    )
    extra = 0
    max_num = 0
    can_delete = True


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    def mesh_id_verbose(self, obj):
        return obj.mesh.verbose_id

    mesh_id_verbose.short_description = "Mesh ID (Verbose)"

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = "Image Count"

    def images_good_count(self, obj):
        return obj.images.filter(label="good").count()

    images_good_count.short_description = "Good Image Count"

    readonly_fields = (
        "ID",
        "mesh",
        "contributor",
        "contributed_at",
        "processed",
        "processed_at",
        "image_count",
        "images_good_count",
    )
    fields = (
        "ID",
        "contributed_at",
        "mesh",
        "contributor",
        "processed",
        "processed_at",
        "image_count",
        "images_good_count",
    )
    list_filter = (
        "processed",
        "mesh",
    )
    list_display = (
        "ID",
        "contributed_at",
        "mesh_id_verbose",
        "contributor",
        "image_count",
        "images_good_count",
        "processed",
    )
    list_per_page = 50
    inlines = [
        ImageInlineContribution,
    ]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    def note(self, obj):
        return (
            "PLEASE USE THE WEB INTERFACE TO ADD IMAGES.\nALSO, USE `Label` FOR MANUAL MODERATION.\n"
            + "ADD A REMARK IN `Remark` IF YOU ARE MANUALLY CHANGING THE LABEL."
        )

    def get_thumbnail(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" style="width: 400px; height: 400px">'
        )

    get_thumbnail.short_description = "Preview"

    def get_mesh_id_verbose(self, obj):
        return obj.contribution.mesh.verbose_id

    get_mesh_id_verbose.short_description = "Mesh ID (Verbose)"

    def get_contributor_link(self, obj):
        url = reverse(
            "admin:tirtha_contributor_change", args=[obj.contribution.contributor.ID]
        )
        return mark_safe(f'<a href="{url}">{obj.contribution.contributor.name}</a>')

    get_contributor_link.short_description = "Link to Contributor"

    @admin.action(description="Mark selected images as Good")
    def mark_good(self, request, queryset):
        updated = queryset.update(label="good")
        self.message_user(
            request,
            ngettext(
                "%d image was successfully marked as Good.",
                "%d images were successfully marked as Good.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Mark selected images as Bad")
    def mark_bad(self, request, queryset):
        updated = queryset.update(label="bad")
        self.message_user(
            request,
            ngettext(
                "%d image was successfully marked as Bad.",
                "%d images were successfully marked as Bad.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Mark selected images as NSFW")
    def mark_nsfw(self, request, queryset):
        updated = queryset.update(label="nsfw")
        self.message_user(
            request,
            ngettext(
                "%d image was successfully marked as NSFW.",
                "%d images were successfully marked as NSFW.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    actions = [mark_good, mark_bad, mark_nsfw]
    readonly_fields = (
        "ID",
        "contribution",
        "created_at",
        "image",
        "note",
        "get_thumbnail",
        "get_mesh_id_verbose",
        "get_contributor_link",
    )
    fieldsets = (
        (
            "Image Details",
            {
                "fields": (
                    ("note"),
                    ("ID"),
                    ("get_mesh_id_verbose"),
                    ("get_contributor_link"),
                    ("contribution"),
                    ("created_at"),
                    ("image", "get_thumbnail"),
                    ("label"),
                    ("remark"),
                )
            },
        ),
    )
    list_filter = ("label",)
    list_display = ("ID", "created_at", "contribution", "label", "get_thumbnail")
    list_per_page = 100


class ImageInlineRun(admin.TabularInline):
    """
    Shows images in the Run admin page

    """

    model = Run.images.through
    extra = 0


class ContributorInlineRun(admin.TabularInline):
    """
    Shows contributors in the Run admin page

    """

    model = Run.contributors.through
    extra = 0


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    def mesh_id_verbose(self, obj):
        return obj.mesh.verbose_id

    mesh_id_verbose.short_description = "Mesh ID (Verbose)"

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = "Image Count"

    readonly_fields = (
        "ID",
        "ark",
        "mesh_id_verbose",
        "started_at",
        "ended_at",
        "image_count",
        "status",
        "directory",
    )
    fieldsets = (
        (
            "Run Details",
            {
                "fields": (
                    ("ID"),
                    ("ark"),
                    ("mesh_id_verbose"),
                    ("status"),
                    ("started_at", "ended_at"),
                    ("directory"),
                    ("image_count"),
                    (
                        "rotaZ",
                        "rotaX",
                        "rotaY",
                    ),  # Used only for <model-viewer>'s orientation
                )
            },
        ),
    )
    list_filter = ("status",)
    list_display = (
        "ID",
        "mesh_id_verbose",
        "image_count",
        "status",
        "started_at",
        "ark",
    )
    list_per_page = 50
    inlines = [ImageInlineRun, ContributorInlineRun]


@admin.register(ARK)
class ARKAdmin(admin.ModelAdmin):
    def mesh_id_verbose(self, obj):
        return obj.run.mesh.verbose_id

    mesh_id_verbose.short_description = "Mesh ID (Verbose)"

    def get_run(self, obj):
        return obj.run

    get_run.short_description = "Run"

    def image_count(self, obj):
        return obj.run.images.count()

    image_count.short_description = "Total Image Count"

    readonly_fields = (
        "ark",
        "get_run",
        "mesh_id_verbose",
        "image_count",
        "naan",
        "shoulder",
        "assigned_name",
        "created_at",
        "url",
        "metadata",
    )
    fieldsets = (
        (
            "ARK Details",
            {
                "fields": (
                    ("ark"),
                    ("url"),
                    ("created_at"),
                    ("get_run"),
                    ("mesh_id_verbose"),
                    ("image_count"),
                    ("naan", "shoulder", "assigned_name"),
                    ("metadata"),
                    ("commitment"),
                )
            },
        ),
    )
    list_display = ("ark", "mesh_id_verbose", "get_run", "created_at", "image_count")
    list_per_page = 50
