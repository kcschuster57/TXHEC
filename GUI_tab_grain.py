import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageOps
from labeled_widgets import LabeledEntryWithUnit, HideableButton
from GRAIN2d import image_path, do_grain_run
import trimesh
from tkinter.filedialog import askopenfilename
import numpy as np
import io
import State as state

class tab_grain(tk.Frame):
    def __init__(self, master):
        super().__init__(master, borderwidth=0)
        self.grain_image_display = None
        self.grain_display = None
        self.create_widgets()

    def create_widgets(self):
        # === FRAMES ===
        self.frame_grain_buttons = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        self.frame_grain_buttons.grid(row=0, column=0)

        self.frame_grain_data = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        self.frame_grain_data.grid(row=1, column=0)

        # === Buttons ===
        self.grain_run_button = HideableButton(
            master=self.frame_grain_buttons, text="Run Grain Sim", showoninit=1,
            command=self.grain_run, height=2, width=15, row=0, column=0
        )
        self.grain_generate_button = HideableButton(
            master=self.frame_grain_buttons, text="Generate Image", showoninit=1,
            command=self.grain_generate, height=2, width=15, row=1, column=0
        )
        self.grain_import_obj_button = HideableButton(
            master=self.frame_grain_buttons, text="Import OBJ", showoninit=1,
            command=self.grain_import_obj, height=2, width=15, row=2, column=0
        )

        # === Grain data entries ===
        self.data_grain_OD = LabeledEntryWithUnit(
            master=self.frame_grain_data, label="Port OD",
            default="0.168275", units=["m","mm","in"], row=0
        )
        self.data_grain_ID = LabeledEntryWithUnit(
            master=self.frame_grain_data, label="Port ID",
            default="0.1016", units=["m","mm","in"], row=1
        )

    def grain_generate(self):
        # Read OD and ID from entries


        grain_OD_m = float(state.convert_by_unit(self.data_grain_OD.get_value(), self.data_grain_OD.get_unit()))
        grain_ID_m = float(state.convert_by_unit(self.data_grain_ID.get_value(), self.data_grain_ID.get_unit()))

        # Compute PIXEL_TO_METER dynamically
        target_pixels = 1000
        pixel_to_meter = grain_OD_m / target_pixels  # dynamic scaling

        # Convert OD and ID to pixels
        grain_OD_px = int(round(grain_OD_m / pixel_to_meter))
        circle_radius_px = int(round(grain_ID_m / (2 * pixel_to_meter)))

        # Create image
        img = Image.new("L", (grain_OD_px, grain_OD_px), 0)
        draw = ImageDraw.Draw(img)
        cx, cy = grain_OD_px // 2, grain_OD_px // 2
        bbox = [cx - circle_radius_px, cy - circle_radius_px, cx + circle_radius_px, cy + circle_radius_px]
        draw.ellipse(bbox, fill=255)
        img.save(image_path)

        # Display in Tkinter
        img_tk = img.resize((400, 400))
        self.grain_image_display = ImageTk.PhotoImage(img_tk)
        if self.grain_display is not None:
            self.grain_display.destroy()
        self.grain_display = tk.Label(self, image=self.grain_image_display)
        self.grain_display.grid(row=0, column=2, rowspan=99)

    def grain_run(self):
        # Read OD and ID from entries
        grain_OD_m = float(state.convert_by_unit(self.data_grain_OD.get_value(), self.data_grain_OD.get_unit()))
        grain_ID_m = float(state.convert_by_unit(self.data_grain_ID.get_value(), self.data_grain_ID.get_unit()))
        do_grain_run(grain_OD_m,grain_ID_m)

    def grain_import_obj(self):
        # Step 1: Choose and load .obj file
        currentfile = askopenfilename(filetypes=[('Grain Object Files', '*.obj')])
        if not currentfile:
            return  # User cancelled
        obj_file_path = currentfile

        # Step 2: Load mesh and generate 2D cross-section
        z_height = 0
        mesh = trimesh.load_mesh(obj_file_path, process=False, maintain_order=True)
        section = mesh.section(plane_origin=[0, 0, z_height], plane_normal=[0, 0, 1])

        if section is None:
            raise ValueError("No cross-section found at z = 0. Check the mesh and plane height.")

        section_2d, _ = section.to_planar()

        # Step 3: Read OD from Tkinter entry (in meters)
        grain_OD_m = float(state.convert_by_unit(self.data_grain_OD.get_value(), self.data_grain_OD.get_unit()))

        # Step 4: Get section bounds (OBJ dimensions in real units)
        min_x, min_y = section_2d.bounds[0]
        max_x, max_y = section_2d.bounds[1]
        width_m = max_x - min_x
        height_m = max_y - min_y

        # Step 5: Compute pixel scaling based on OD
        # The OD defines how many meters correspond to 1000 pixels
        target_pixels = 1000
        pixel_to_meter = grain_OD_m / target_pixels

        # Convert OBJ dimensions to pixels (without rescaling mesh)
        width_px = int(round(width_m / pixel_to_meter))
        height_px = int(round(height_m / pixel_to_meter))

        # Step 6: Center the mesh footprint in a 1000x1000 canvas
        canvas_px = target_pixels
        img = Image.new("L", (canvas_px, canvas_px), 0)
        draw = ImageDraw.Draw(img)

        # Translate section to start at (0, 0)
        section_2d.apply_translation(-np.array([min_x, min_y]))

        # Compute placement offsets to center the mesh
        x_offset = (canvas_px - width_px) // 2
        y_offset = (canvas_px - height_px) // 2

        # Step 7: Draw the section polygons at the correct pixel scale
        for poly in section_2d.polygons_full:
            scaled_coords = [
                (x / pixel_to_meter + x_offset, canvas_px - (y / pixel_to_meter + y_offset))
                for x, y in np.array(poly.exterior.coords)
            ]
            draw.polygon(scaled_coords, fill=255)

            for hole in poly.interiors:
                hole_coords = [
                    (x / pixel_to_meter + x_offset, canvas_px - (y / pixel_to_meter + y_offset))
                    for x, y in np.array(hole.coords)
                ]
                draw.polygon(hole_coords, fill=0)

        # Step 8: Save and display in Tkinter
        the_image_path = image_path
        img.save(the_image_path)

        img_tk = img.resize((400, 400))
        self.grain_image_display = ImageTk.PhotoImage(img_tk)

        if hasattr(self, "grain_display") and self.grain_display is not None:
            self.grain_display.destroy()

        self.grain_display = tk.Label(self, image=self.grain_image_display)
        self.grain_display.grid(row=0, column=2, rowspan=99)

        print("Imported OBJ cross-section saved as:", image_path)
        print(f"OBJ real size: {width_m:.6f} m x {height_m:.6f} m, displayed using OD={grain_OD_m:.6f} m")
        print(f"pixel_to_meter = {pixel_to_meter:.6e} (larger OD = smaller visual footprint)")
