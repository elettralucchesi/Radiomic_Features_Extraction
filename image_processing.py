import os
import numpy as np
import SimpleITK as sitk
from scipy.ndimage import label

def extract_largest_region(mask_slice, label_value):
    """
    Extract the largest connected region of a given label from a binary mask slice.

    :param mask_slice: 2D numpy array representing the mask slice
    :param label_value: Integer label to extract the largest region from
    :return: 2D numpy array containing only the largest connected region of the given label
    """

    # Check if inputs are swapped (i.e., label_value is a numpy array and mask_slice is an integer)
    if isinstance(mask_slice, int) and isinstance(label_value, np.ndarray):
        raise TypeError(
            "Inputs appear to be swapped. Expected mask_slice as a numpy array and label_value as an integer.")

    if not isinstance(label_value, int):
        raise TypeError("Label value must be an integer")
    if label_value < 0:
        raise ValueError("Label value cannot be negative")

    # Create a binary mask for the specified label
    region_mask = (mask_slice == label_value)

    # Label the connected components in the binary mask
    labeled_region, num_labels = label(region_mask)

    largest_region = None
    largest_area = 0

    # Iterate through all connected components, ignoring the background (0)
    for region_id in range(1, num_labels + 1):
        region = (labeled_region == region_id).astype(mask_slice.dtype) * label_value
        region_area = np.sum(region > 0)

        # Update the largest region if the current one is bigger
        if region_area > largest_area:
            largest_area = region_area
            largest_region = region

    return largest_region


def process_slice(mask_slice):
    """
    Process a mask slice to extract the largest connected region for each label.

    :param mask_slice: 2D numpy array representing the mask slice
    :return: Tuple (largest_region_mask, label) of the largest region found
    :raises ValueError: If the mask has no labeled regions
    """

    labels = np.unique(mask_slice)
    labels = labels[labels != 0]  # Exclude background

    for lbl in labels:
        lbl = int(lbl)  # Convert numpy.int16 to native Python int
        largest_region_mask = extract_largest_region(mask_slice, lbl)
        if largest_region_mask is not None:
            return largest_region_mask, lbl
    # If no region found
    return None, None


def get_slices_2D(image, mask, patient_id):

    if not isinstance(image, sitk.Image):
        raise TypeError(f"Expected 'image' to be a SimpleITK Image, but got {type(image)}.")

    if not isinstance(mask, sitk.Image):
        raise TypeError(f"Expected 'mask' to be a SimpleITK Image, but got {type(mask)}.")

    # Verifica che patient_id sia una stringa
    if not isinstance(patient_id, int):
        raise ValueError(f"Expected 'patient_id' to be a int, but got {type(patient_id)}.")

    image_array = sitk.GetArrayFromImage(image)
    mask_array = sitk.GetArrayFromImage(mask)
    patient_slices = []

    for slice_idx in range(mask_array.shape[0]):
        mask_slice = mask_array[slice_idx, :, :]
        image_slice = image_array[slice_idx, :, :]

        region_mask, region_label = process_slice(mask_slice)
        if region_mask is None:
            continue
        largest_region_mask_image  = sitk.GetImageFromArray(region_mask)
        image_slice_image = sitk.GetImageFromArray(image_slice)
        patient_slices.append({
            'PatientID': f"PR{patient_id}",
            'Label': region_label,
            'SliceIndex': slice_idx,
            'ImageSlice':  image_slice_image,
            'MaskSlice': largest_region_mask_image
        })

    return patient_slices


def get_volume_3D(image, mask, patient_id):

    if not isinstance(image, sitk.Image):
        raise TypeError(f"Expected 'image' to be a SimpleITK Image, but got {type(image)}.")

    if not isinstance(mask, sitk.Image):
        raise TypeError(f"Expected 'mask' to be a SimpleITK Image, but got {type(mask)}.")

    if not isinstance(patient_id, int):
        raise ValueError(f"Expected 'patient_id' to be a int, but got {type(patient_id)}.")

    return [{
        'PatientID': f"PR{patient_id}",
        'ImageVolume': image,
        'MaskVolume': mask
    }]



def read_image_and_mask(image_path, mask_path):
    """
    Read an image and its corresponding mask using SimpleITK.

    :param image_path: Path to the image file.
    :param mask_path: Path to the mask file.
    :return: Tuple containing the image and mask as SimpleITK images.
    :raises ValueError: If any of the input paths is empty.
    :raises TypeError: If the input paths are not strings.
    :raises ValueError: If the parent directories of the image and mask do not match.
    :raises ValueError: If the image and mask dimensions do not match.
    """

    if not image_path or not mask_path:
        raise ValueError("Image and mask paths cannot be empty.")

    if not isinstance(image_path, str) or not isinstance(mask_path, str):
        raise TypeError("Image and mask paths must be strings.")

    if os.path.dirname(image_path) != os.path.dirname(mask_path):
        raise ValueError("Image and mask must be in the same directory.")

    img = sitk.ReadImage(image_path)
    mask = sitk.ReadImage(mask_path)

    if img.GetSize() != mask.GetSize():
        raise ValueError("Image and mask dimensions do not match.")

    return img, mask



def get_patient_image_mask_dict(imgs_path, masks_path, patient_ids, mode):
    if len(patient_ids) == 0:
        raise ValueError("The patient_ids list cannot be empty.")

    if len(imgs_path) != len(masks_path) or len(imgs_path) != len(patient_ids):
        raise ValueError("The number of images, masks, and patient_ids must be the same.")

    patient_dict = {}

    for pr_id, img_path, mask_path in zip(patient_ids, imgs_path, masks_path):
        img, mask = read_image_and_mask(img_path, mask_path)

        if mode == "2D":
            patient_slices = get_slices_2D(img, mask, pr_id)
            patient_dict[pr_id] = patient_slices
        elif mode == "3D":
            patient_volume = get_volume_3D(img, mask, pr_id)
            patient_dict[pr_id] = patient_volume
        else:
            raise ValueError("Mode should be '2D' or '3D'")

    return patient_dict