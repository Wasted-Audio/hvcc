# Heavy Compiler Collection
# Copyright (C) 2026 Wasted Audio
#
# SPDX-License-Identifier: GPL-3.0-only

import math

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

from PIL import Image

from hvcc.generators.c2meta.meta_types import Coords, Panel, Assets, Size, UIElement


PANEL_HEIGHT = 240
PANEL_MIN_WIDTH = 20

PADDING_X = 10
PADDING_Y = 10
MARGIN_X = 10
MARGIN_Y = 20


@lru_cache(maxsize=None)
def image_size(image: Path) -> tuple[int, int]:
    return Image.open(image).size


@dataclass
class Shelf:
    """A single sub-row within a category: a horizontal strip of items."""
    items: list[UIElement]
    height: int


@dataclass
class CategoryInfo:
    """Layout state for one category (knobs, leds, inputs, or outputs)."""
    items: list[UIElement]
    max_w: int = 0
    max_h: int = 0
    rows: int = 1
    shelves: list[Shelf] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def height_at_current_rows(self) -> int:
        """Vertical space this category occupies given its current row count."""
        if self.rows == 0:
            return 0
        return self.rows * self.max_h + (self.rows - 1) * PADDING_Y

    @property
    def shelf_demand(self) -> float:
        """Vertical space this category's actual shelves need, once built."""
        if not self.shelves:
            return 0.0
        return sum(s.height for s in self.shelves) + (len(self.shelves) - 1) * PADDING_Y


@dataclass
class Grid:
    col_center_x: list[float]
    panel_width: int
    single_column: bool


def _compute_grid(cat_infos: list[CategoryInfo]) -> Grid:
    """
    Derive the shared column grid from every category's shelves: the
    number of columns needed (the widest shelf across all categories),
    each column's center x-axis, and the resulting panel width.
    """
    max_cols = max(
        (len(shelf.items) for info in cat_infos for shelf in info.shelves),
        default=1,
    )
    col_width = max((c.max_w for c in cat_infos if c.max_w > 0), default=0)
    col_center_x = [
        MARGIN_X + col * (col_width + PADDING_X) + col_width / 2.0
        for col in range(max_cols)
    ]
    panel_width = round(MARGIN_X * 2 + max_cols * col_width + (max_cols - 1) * PADDING_X)

    return Grid(col_center_x, panel_width, single_column=max_cols == 1)


def _allocate_heights(cat_infos: list[CategoryInfo], available_h: int) -> list[float]:
    """
    Split the available vertical space between categories in proportion
    to each category's shelf_demand. Categories with no shelves get 0.
    """
    total_demand = sum(c.shelf_demand for c in cat_infos)
    return [
        (c.shelf_demand / total_demand) * available_h if c.shelf_demand > 0 else 0.0
        for c in cat_infos
    ]


def _gather_category_info(category_lists: list[list]) -> list[CategoryInfo]:
    """
    Build a CategoryInfo for each category, recording item count and the
    max item width/height within that category. Empty categories get
    rows=0 so they're skipped by later layout steps.
    """
    infos = []
    for items in category_lists:
        if not len(items):
            infos.append(CategoryInfo(items=items, rows=0))
            continue

        sizes = [image_size(item.image) for item in items]
        infos.append(CategoryInfo(
            items=items,
            max_w=max(w for w, _ in sizes),
            max_h=max(h for _, h in sizes),
            rows=1,
        ))

    return infos


def _distribute_extra_rows(cat_infos: list[CategoryInfo], available_h: int) -> None:
    """
    Greedily give categories extra sub-rows as long as there's vertical space
    left, always picking whichever split relieves the most crowded row.
    """
    while True:
        total_h = sum(c.height_at_current_rows for c in cat_infos)

        best_candidate: Optional[CategoryInfo] = None
        best_items_per_row = 0

        for c in cat_infos:
            if c.count <= 1 or c.rows >= c.count:
                continue  # can't split further

            extra_h = c.max_h + PADDING_Y
            if total_h + extra_h > available_h:
                continue  # no room for another row

            items_per_row = math.ceil(c.count / c.rows)
            if items_per_row > best_items_per_row:
                best_items_per_row = items_per_row
                best_candidate = c

        if best_candidate is None:
            break
        best_candidate.rows += 1


def _build_shelves(info: CategoryInfo) -> None:
    """Split a category's items evenly across its allotted number of rows."""
    if info.rows == 0 or not info.items:
        return

    items_per_shelf = math.ceil(info.count / info.rows)

    for start in range(0, info.count, items_per_shelf):
        shelf_items = info.items[start:start + items_per_shelf]
        shelf_h = max(image_size(item.image)[1] for item in shelf_items)
        info.shelves.append(Shelf(items=shelf_items, height=shelf_h))


def _place_shelf_items(
    shelf: Shelf,
    shelf_center_y: float,
    col_center_x: list[float],
    panel_width: int,
    single_column_panel: bool,
) -> None:
    """
    Walk each category top-to-bottom through its allocated height slice,
    dividing it evenly across the category's shelves, and place every
    item on its shelf using the shared column grid.
    """
    if len(shelf.items) == 1 and single_column_panel:
        # Whole panel is one column wide -> center this lone item on the panel.
        item = shelf.items[0]
        img_w, img_h = image_size(item.image)
        item.coords = Coords(
            x=round((panel_width - img_w) / 2.0),
            y=round(shelf_center_y - img_h / 2.0),
        )
        return

    # Otherwise align each item to its column's center axis.
    for col, item in enumerate(shelf.items):
        img_w, img_h = image_size(item.image)
        item.coords = Coords(
            x=round(col_center_x[col] - img_w / 2.0),
            y=round(shelf_center_y - img_h / 2.0),
        )


def _place_items(
    cat_infos: list[CategoryInfo],
    allocated_heights: list[float],
    grid: Grid
) -> None:
    """
    Place every item: centered on its column axis (or on the whole panel
    when there's only one column anywhere and only one item on the shelf).
    """
    current_y = float(MARGIN_Y)

    for info, allocated_h in zip(cat_infos, allocated_heights):
        if not info.shelves or allocated_h == 0:
            continue

        slot_h = allocated_h / len(info.shelves)
        for i, shelf in enumerate(info.shelves):
            shelf_center_y = current_y + i * slot_h + slot_h / 2.0
            _place_shelf_items(
                shelf, shelf_center_y, grid.col_center_x, grid.panel_width, grid.single_column
            )

        current_y += allocated_h


def layout_panel_assets(assets: Assets) -> Assets:
    """
    Layout algorithm with column center alignment.
    Aligns knobs, jacks, and leds along standard vertical column axes.
    """
    cat_infos = _gather_category_info(
        [assets.knobs, assets.leds, assets.inputs, assets.outputs]
    )

    if not any(c.count for c in cat_infos):
        assets.panel = Panel(size=Size(x=PANEL_MIN_WIDTH, y=PANEL_HEIGHT))
        return assets

    available_h = PANEL_HEIGHT - (MARGIN_Y * 2)

    _distribute_extra_rows(cat_infos, available_h)

    for info in cat_infos:
        _build_shelves(info)

    grid = _compute_grid(cat_infos)
    allocated_heights = _allocate_heights(cat_infos, available_h)
    _place_items(cat_infos, allocated_heights, grid)

    assets.panel = Panel(size=Size(x=grid.panel_width, y=PANEL_HEIGHT))

    return assets
