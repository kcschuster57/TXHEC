import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy import ndimage as ndi
from scipy.ndimage import uniform_filter1d
from PIL import Image, ImageDraw
import os

import State as state

image_path = "grain_image.png"

def do_grain_run(grain_OD_m, grain_ID_m):
    target_pixels = 1000
    pixel_to_meter = grain_OD_m / target_pixels  # dynamic scaling
    scale = 1 / pixel_to_meter

    def meters_to_pixels(m):
        return int(m * scale)

    def create_circle_grain(grain_diameter, boundary_diameter):
        grid_size = meters_to_pixels(boundary_diameter)
        radius_pixels = meters_to_pixels(grain_diameter / 2)
        image = np.zeros((grid_size, grid_size), dtype=np.uint8)
        Y, X = np.ogrid[:grid_size, :grid_size]
        center = grid_size // 2
        mask = (X - center) ** 2 + (Y - center) ** 2 <= radius_pixels ** 2
        image[mask] = 1
        return image

    def crop_fill_and_expand(image_path, boundary_diameter_meters):
        img = Image.open(image_path).convert("L")
        binary_image = (np.array(img) > 128).astype(np.uint8)
        coords = np.column_stack(np.where(binary_image == 1))
        if coords.size == 0:
            raise ValueError("No shape found in PNG.")
        min_y, min_x = coords.min(axis=0)
        max_y, max_x = coords.max(axis=0)
        cropped = binary_image[min_y:max_y + 1, min_x:max_x + 1]
        filled = ndi.binary_fill_holes(cropped).astype(np.uint8)
        filled_pil = Image.fromarray((1 - filled) * 255)
        grid_size = meters_to_pixels(boundary_diameter_meters)
        expanded = Image.new("L", (grid_size, grid_size), 255)
        px = (grid_size - filled_pil.width) // 2
        py = (grid_size - filled_pil.height) // 2
        expanded.paste(filled_pil, (px, py))
        return (np.array(expanded) < 128).astype(int)

    def fast_marching_method(boundary):
        return ndi.distance_transform_edt(boundary == 0)

    def touches_image_boundary(mask):
        return mask[0, :].any() or mask[-1, :].any() or mask[:, 0].any() or mask[:, -1].any()

    def calculate_perimeter(distance_field, distance_thresholds):
        perimeter = []
        for threshold in distance_thresholds:
            mask = (distance_field <= threshold) & (distance_field > (threshold - 1))
            boundary_points = ndi.binary_erosion(mask) != mask
            perimeter_pixels = np.sum(boundary_points)
            perimeter.append(perimeter_pixels * pixel_to_meter)
        return perimeter

    # Choose data source
    if image_path and os.path.exists(image_path):
        boundary = crop_fill_and_expand(image_path, grain_OD_m)
    else:
        boundary = create_circle_grain(grain_ID_m, grain_OD_m)

    distance_field = fast_marching_method(boundary)
    circle_radius_pixels = meters_to_pixels(grain_OD_m / 2)
    distance_field[distance_field > circle_radius_pixels] = np.inf
    distance_field = np.where(np.isinf(distance_field), circle_radius_pixels, distance_field)

    distance_thresholds = []
    perimeter_values = []
    area_values = []  # store area (m^2) for each regression step

    for threshold in range(int(np.max(distance_field))):
        mask = (distance_field <= threshold)
        if touches_image_boundary(mask):
            break
        distance_thresholds.append(threshold)
        perimeter_values.append(calculate_perimeter(distance_field, [threshold])[0])

        # --- Area calculation ---
        area_pixels = np.sum(mask)
        area_m2 = area_pixels * (pixel_to_meter ** 2)
        area_values.append(area_m2)

        # Console readout
        #print(f"Step {threshold:4d} | Regression: {threshold * pixel_to_meter:.6f} m | Area: {area_m2:.8f} m^2")

    distance_thresholds = np.array(distance_thresholds)

    # --- Regression and Smoothing ---
    np_regression = distance_thresholds * pixel_to_meter
    np_perimeter = np.array(perimeter_values)
    np_area = np.array(area_values)

    window_size = 21
    smoothed_perimeter = uniform_filter1d(np_perimeter, size=window_size, mode='reflect')

    #Interactive Visualization
    fig, axs = plt.subplots(1, 2, figsize=(11, 5))
    plt.subplots_adjust(bottom=0.25)

    #Left: grain boundary image (dynamic)
    im_boundary = axs[0].imshow(boundary, cmap='gray')
    axs[0].set_title("Grain Regression Visualization")
    axs[0].axis('off')

    #Right: perimeter vs regression (static)
    axs[1].plot(np_regression, np_perimeter, 'r', alpha=0.5, label="Raw")
    axs[1].plot(np_regression, smoothed_perimeter, 'b', label="Smoothed")
    axs[1].set_xlabel("Total Regression (m)")
    axs[1].set_ylabel("Perimeter (m)")
    axs[1].set_title("Perimeter vs Regression")
    axs[1].legend()
    axs[1].grid(True)

    #Slider axis
    ax_slider = plt.axes([0.25, 0.1, 0.5, 0.03])
    slider = Slider(ax_slider, 'Regression (m)', 0, np_regression[-1],
                    valinit=0, valstep=pixel_to_meter)

    def update(val):
        threshold_m = slider.val
        threshold_px = int(threshold_m / pixel_to_meter)
        mask = (distance_field <= threshold_px)
        if touches_image_boundary(mask):
            print(f"Touch at {threshold_m:.6f} m - stop.")
            return
        new_image = np.copy(boundary)
        new_image[mask] = 1
        im_boundary.set_data(new_image)
        fig.canvas.draw_idle()

    slider.on_changed(update)


    print("Interactive plot ready.")

    state.grain_OD_m = grain_OD_m
    state.grain_regression = np_regression
    state.grain_perimeter = smoothed_perimeter
    state.grain_area = np_area
    state.grain_config = 1
    state.tab_tc_ref.clear_grain_hold()
    
    cleanup_files()
    plt.show()
    return np_regression, np_perimeter, np_area

def cleanup_files():
    state.delete_file(image_path)
