import pytest
import numpy as np
import SimpleITK as sitk
from unittest.mock import patch
from image_processing import *


def test_extract_largest_region_correct():
    """
    Test the correct behavior of the extract_largest_region function.

    GIVEN: A 2D binary mask with two regions of a specified label.
    WHEN: The extract_largest_region function is called.
    THEN: The function correctly returns the largest connected region.
    """
    mask = np.array([[1, 1, 0, 0],
                     [1, 1, 0, 0],
                     [1, 0, 1, 1],
                     [0, 0, 1, 1]])

    label_value = 1
    largest_region = extract_largest_region(mask, label_value)

    expected = np.array([[1, 1, 0, 0],
                         [1, 1, 0, 0],
                         [1, 0, 0, 0],
                         [0, 0, 0, 0]])

    # Assert the largest region is correctly extracted
    assert np.array_equal(largest_region, expected), f"Expected largest region {expected}, but got {largest_region}"


def test_extract_largest_region_negative_label():
    """
    Test that the function raises an error when the label value is negative.

    GIVEN: A negative label value.
    WHEN: The extract_largest_region function is called.
    THEN: The function should raise a ValueError indicating the label cannot be negative.
    """
    mask_slice = np.array([[1, 1, 0, 0],
                     [1, 1, 0, 0],
                     [1, 0, 1, 1],
                     [0, 0, 1, 1]])  # Valid mask slice
    label_value = -1  # Invalid label value

    try:
        extract_largest_region(mask_slice, label_value)
    except ValueError as e:
        assert str(e) == "Label value cannot be negative", "Error message does not match."


def test_extract_largest_region_label_not_found():
    """
    Test that the function returns None when the label is not found in the mask slice.

    GIVEN: A mask slice with no regions for the specified label.
    WHEN: The extract_largest_region function is called.
    THEN: The function should return None, as the label does not exist in the mask.
    """
    mask_slice = np.array([[2, 2, 0, 0],
                     [2, 2, 0, 0],
                     [2, 0, 3, 3],
                     [0, 0, 3, 3]])  # Valid mask slice
    label_value = 1  # Label not present

    result = extract_largest_region(mask_slice, label_value)

    assert result is None, "The function should return None when the label is not found."


def test_extract_largest_region_found():
    """
    Test that the function correctly extracts the largest region of a given label.

    GIVEN: A mask slice with several regions for the specified label.
    WHEN: The extract_largest_region function is called.
    THEN: The function should return the largest region of the given label.
    """
    mask_slice = np.array([
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 2, 2, 2],
        [0, 0, 2, 2, 2],
        [0, 0, 0, 0, 0]
    ], dtype=int)  # Two regions: Label 1 and Label 2
    label_value = 1

    result = extract_largest_region(mask_slice, label_value)

    # The largest region should be of label 1
    expected_result = np.array([
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ], dtype=int)

    assert np.array_equal(result,
                          expected_result), "The function should extract the largest connected region for label 1."


def test_extract_largest_region_swapped_inputs():
    """
    Test that the function raises an error when the inputs are swapped.

    GIVEN: The function is called with an integer as mask_slice and a numpy array as label_value.
    WHEN: The extract_largest_region function is called with incorrect argument order.
    THEN: The function should raise a TypeError indicating the inputs are swapped.
    """
    mask_slice = 1  # Incorrect: should be a numpy array
    label_value = np.array([[0, 1], [1, 0]])  # Incorrect: should be an integer

    try:
        extract_largest_region(mask_slice, label_value)
    except TypeError as e:
        assert str(e) == "Inputs appear to be swapped. Expected mask_slice as a numpy array and label_value as an integer.", \
            "Error message does not match."


def test_extract_largest_region_label_not_float():
    """
    Test that the function raises a TypeError if label_value is a float.

    GIVEN: A float label value.
    WHEN: The extract_largest_region function is called.
    THEN: The function should raise a TypeError indicating that the label value must be an integer.
    """
    mask_slice = np.zeros((5, 5), dtype=int)  # Example empty mask slice

    # Test with a float as label_value
    label_value = 1.5
    with pytest.raises(TypeError, match="Label value must be an integer"):
        extract_largest_region(mask_slice, label_value)


def test_extract_largest_region_label_not_string():
    """
    Test that the function raises a TypeError if label_value is a string.

    GIVEN: A string label value.
    WHEN: The extract_largest_region function is called.
    THEN: The function should raise a TypeError indicating that the label value must be an integer.
    """
    mask_slice = np.zeros((5, 5), dtype=int)  # Example empty mask slice

    # Test with a string as label_value
    label_value = "label"
    with pytest.raises(TypeError, match="Label value must be an integer"):
        extract_largest_region(mask_slice, label_value)



def test_process_slice_single_label():
    """
    Test process_slice with a mask containing a single labeled region.

    GIVEN: A mask with a single labeled region.
    WHEN: The function is called.
    THEN: It should return the largest region mask and its corresponding label.
    """
    mask_slice = np.array([
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]
    ])

    largest_region_mask, label = process_slice(mask_slice)
    assert label == 1, "Expected label 1, but got a different label."


def test_process_slice_single_mask():
    """
    Test process_slice with a mask containing a single labeled region.

    GIVEN: A mask with a single labeled region.
    WHEN: The function is called.
    THEN: It should return the largest region mask and its corresponding label.
    """
    mask_slice = np.array([
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]
    ])

    largest_region_mask, label = process_slice(mask_slice)

    # Verify that the largest region mask matches the expected result
    expected_region_mask = np.array([
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]
    ])
    assert np.array_equal(largest_region_mask,
                          expected_region_mask), "The largest region mask does not match the expected result."


def test_process_slice_multiple_labels_label():
    """
    Test that the function correctly returns the largest region mask and its corresponding label when there are multiple labeled regions.

    GIVEN: A mask slice with multiple labeled regions.
    WHEN: The process_slice function is called.
    THEN: The function should return the largest valid region and its corresponding label.
    """
    mask_slice = np.array([
        [0, 1, 1, 0, 2, 2, 2],
        [0, 1, 1, 0, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0]
    ])

    largest_region_mask, label = process_slice(mask_slice)
    assert label in [1, 2], "Expected label 1 or 2, but got a different label."


def test_process_slice_multiple_labels_mask():
    """
    Test that the function correctly returns the largest region mask and its corresponding label when there are multiple labeled regions.

    GIVEN: A mask slice with multiple labeled regions.
    WHEN: The process_slice function is called.
    THEN: The function should return the largest valid region and its corresponding label.
    """
    mask_slice = np.array([
        [0, 1, 1, 0, 2, 2, 2],
        [0, 1, 1, 0, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0]
    ])

    largest_region_mask, label = process_slice(mask_slice)

    # Define expected region masks for label 1 and label 2
    expected_region_mask_1 = np.array([
        [0, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ])

    expected_region_mask_2 = np.array([
        [0, 0, 0, 0, 2, 2, 2],
        [0, 0, 0, 0, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0]
    ])

    # Assert that the largest region mask matches the expected result based on the label
    assert np.array_equal(largest_region_mask, expected_region_mask_1) or np.array_equal(largest_region_mask,
                                                                                         expected_region_mask_2), \
        f"Unexpected largest region mask for label {label}."


def test_process_slice_returns_none_none():
    """
    GIVEN a mask slice with no labeled regions (all zeros)
    WHEN process_slice is called
    THEN it should return (None, None)
    """
    # Create a 2D mask with only background (all values set to zero)
    mask_slice = np.zeros((10, 10), dtype=np.uint16)

    # Call the process_slice function
    region_mask, label = process_slice(mask_slice)

    # Check that the result is (None, None) with a single assert
    assert (region_mask, label) == (None, None), f"Expected (None, None), but got ({region_mask}, {label})"


def test_get_slices_2D_valid_length():
    """
    Test that get_slices_2D returns the expected number of slices for a valid input.

    GIVEN: A valid image and mask.
    WHEN: The function get_slices_2D is called.
    THEN: It should return a list with the correct number of slices.
    """
    image_array = np.random.rand(3, 4, 4)  # 3 slices, 4x4 pixels
    mask_array = np.array([  # 3 slices, label 1 and 2
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ])
    image = sitk.GetImageFromArray(image_array)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234

    slices = get_slices_2D(image, mask, patient_id)

    assert len(slices) == 3, f"Expected 3 slices, but got {len(slices)}."


def test_get_slices_2D_patient_id():
    """
    Test that the PatientID is correctly set in the slice data.

    GIVEN: A valid image, mask, and PatientID.
    WHEN: The function get_slices_2D is called.
    THEN: The PatientID should be included correctly in each slice data.
    """
    image_array = np.random.rand(3, 4, 4)
    mask_array = np.array([  # 3 slices
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ])
    image = sitk.GetImageFromArray(image_array)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234

    slices = get_slices_2D(image, mask, patient_id)

    assert slices[0]['PatientID'] == f"PR{patient_id}", f"Expected PatientID 'PR{patient_id}', but got {slices[0]['PatientID']}."


def test_get_slices_2D_slice_index():
    """
    Test that the SliceIndex is correctly set in the slice data.

    GIVEN: A valid image, mask, and PatientID.
    WHEN: The function get_slices_2D is called.
    THEN: The SliceIndex should be correctly set for each slice.
    """
    image_array = np.random.rand(3, 4, 4)
    mask_array = np.array([  # 3 slices
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ])
    image = sitk.GetImageFromArray(image_array)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234

    slices = get_slices_2D(image, mask, patient_id)

    assert slices[1]['SliceIndex'] == 1, f"Expected slice index 1, but got {slices[1]['SliceIndex']}."


def test_get_slices_2D_image_slice():
    """
    Test that the image slice is correctly converted into a SimpleITK Image.

    GIVEN: A valid image and mask.
    WHEN: The function get_slices_2D is called.
    THEN: The 'ImageSlice' in the returned data should be a SimpleITK Image.
    """
    image_array = np.random.rand(3, 4, 4)
    mask_array = np.array([  # 3 slices
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ])
    image = sitk.GetImageFromArray(image_array)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234

    slices = get_slices_2D(image, mask, patient_id)

    assert isinstance(slices[0]['ImageSlice'], sitk.Image), "Expected 'ImageSlice' to be a SimpleITK Image."


def test_get_slices_2D_mask_slice():
    """
    Test that the mask slice is correctly converted into a SimpleITK Image.

    GIVEN: A valid image and mask.
    WHEN: The function get_slices_2D is called.
    THEN: The 'MaskSlice' in the returned data should be a SimpleITK Image.
    """
    image_array = np.random.rand(3, 4, 4)
    mask_array = np.array([  # 3 slices
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ])
    image = sitk.GetImageFromArray(image_array)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234

    slices = get_slices_2D(image, mask, patient_id)

    assert isinstance(slices[0]['MaskSlice'], sitk.Image), "Expected 'MaskSlice' to be a SimpleITK Image."


def test_get_slices_2D_labels():
    """
    Test that the correct labels are assigned to the slices.

    GIVEN: A valid image and mask.
    WHEN: The function get_slices_2D is called.
    THEN: The label should be correctly assigned to each slice.
    """
    image_array = np.random.rand(3, 4, 4)
    mask_array = np.array([  # 3 slices
        [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[2, 2, 0, 0], [2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    ])
    image = sitk.GetImageFromArray(image_array)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234
    slices = get_slices_2D(image, mask, patient_id)
    assert slices[0]['Label'] == 1, f"Expected label 1 for first slice, but got {slices[0]['Label']}."


def test_get_slices_2D_invalid_image_type():
    """
    Test that a TypeError is raised when the 'image' is not a SimpleITK Image.

    GIVEN: A non-SimpleITK object for 'image'.
    WHEN: The function get_slices_2D is called.
    THEN: A TypeError should be raised.
    """
    mask_array = np.random.rand(3, 4, 4)
    mask = sitk.GetImageFromArray(mask_array)
    patient_id = 1234

    with pytest.raises(TypeError, match="Expected 'image' to be a SimpleITK Image"):
        get_slices_2D("invalid_image", mask, patient_id)


def test_get_slices_2D_skip_slice_on_none():
    """
    GIVEN a mask slice where process_slice returns None, None (no region found)
    WHEN get_slices_2D is called
    THEN it should skip that slice and not include it in the results
    """
    # Create a 3D image and mask where one slice will have no region
    img = sitk.GetImageFromArray(np.random.rand(3, 10, 10))  # 3 slices
    mask = sitk.GetImageFromArray(np.array([np.zeros((10, 10)), np.zeros((10, 10)), np.ones((10, 10))],
                                           dtype=np.uint16))  # Only last slice has region

    # Mock patient ID
    patient_id = 123

    # Mock the process_slice function to return (None, None) for the first two slices and valid results for the last slice
    with patch('image_processing.process_slice', side_effect=[(None, None), (None, None), (np.ones((10, 10)), 1)]):
        result = get_slices_2D(img, mask, patient_id)

    # Assert that the result contains only one slice (the third slice where the region was found)
    assert len(result) == 1, f"Expected 1 slice, but got {len(result)}"


def test_invalid_mask_type():
    """
    Test that the function raises a TypeError if the mask is not a SimpleITK Image.

    GIVEN: An invalid mask type.
    WHEN: The get_slices_2D function is called.
    THEN: The function should raise a TypeError indicating the invalid mask type.
    """
    valid_image = sitk.Image(10, 10, 10, sitk.sitkUInt8)  # Valid SimpleITK image
    invalid_mask = "invalid_mask"  # A string, not a SimpleITK Image
    patient_id = 1234

    with pytest.raises(TypeError, match="Expected 'mask' to be a SimpleITK Image"):
        get_slices_2D(valid_image, invalid_mask, patient_id)

def test_invalid_patient_id_type():
    """
    Test that the function raises a ValueError if the patient_id is not int.

    GIVEN: A string patient_id.
    WHEN: The get_slices_2D function is called.
    THEN: The function should raise a ValueError indicating the invalid patient_id type.
    """
    valid_image = sitk.Image(10, 10, 10, sitk.sitkUInt8)  # Valid SimpleITK image
    valid_mask = sitk.Image(10, 10, 10, sitk.sitkUInt8)  # Valid SimpleITK mask
    invalid_patient_id = '12345'  # Not a string

    with pytest.raises(ValueError, match="Expected 'patient_id' to be a int"):
        get_slices_2D(valid_image, valid_mask, invalid_patient_id)


def test_get_volume_3D_return_type():
    """
    GIVEN: A 3D image and mask.
    WHEN: The get_volume_3D function is called.
    THEN: The function should return a list containing a dictionary with the correct keys.
    """
    image_3d = sitk.Image(3, 3, 3, sitk.sitkUInt8)
    mask_3d = sitk.Image(3, 3, 3, sitk.sitkUInt8)
    patient_id = 1234

    result = get_volume_3D(image_3d, mask_3d, patient_id)

    assert isinstance(result, list), f"Expected result to be a list, but got {type(result)}."

def test_get_volume_3D_invalid_image_type():
    """
    GIVEN: A non-SimpleITK image (e.g., a numpy array).
    WHEN: The get_volume_3D function is called.
    THEN: The function should raise a TypeError indicating that the image is not of type SimpleITK.Image.
    """
    invalid_image = np.array([[1, 2], [3, 4]])
    mask_3d = sitk.Image(3, 3, 3, sitk.sitkUInt8)
    patient_id = 1234

    with pytest.raises(TypeError, match="Expected 'image' to be a SimpleITK Image"):
        get_volume_3D(invalid_image, mask_3d, patient_id)

def test_get_volume_3D_invalid_image_type():
    """
    GIVEN: A non-SimpleITK image (e.g., a numpy array).
    WHEN: The get_volume_3D function is called.
    THEN: The function should raise a TypeError indicating that the image is not of type SimpleITK.Image.
    """
    invalid_image = np.array([[1, 2], [3, 4]])
    mask_3d = sitk.Image(3, 3, 3, sitk.sitkUInt8)
    patient_id = 1234

    with pytest.raises(TypeError, match="Expected 'image' to be a SimpleITK Image"):
        get_volume_3D(invalid_image, mask_3d, patient_id)

def test_get_volume_3D_invalid_patient_id():
    """
    GIVEN: A string patient_id.
    WHEN: The get_volume_3D function is called.
    THEN: The function should raise a ValueError indicating that patient_id must be int.
    """
    image_3d = sitk.Image(3, 3, 3, sitk.sitkUInt8)
    mask_3d = sitk.Image(3, 3, 3, sitk.sitkUInt8)
    patient_id = '123'

    with pytest.raises(ValueError, match="Expected 'patient_id' to be a int"):
        get_volume_3D(image_3d, mask_3d, patient_id)



def test_get_patient_image_mask_dict_empty_patient_ids():
    """
    GIVEN: An empty list for patient_ids.
    WHEN: The get_patient_image_mask_dict function is called.
    THEN: The function should raise a ValueError indicating that the patient_ids list cannot be empty.
    """
    imgs_path = ["img1.nii", "img2.nii"]
    masks_path = ["mask1.nii", "mask2.nii"]
    patient_ids = []  # Empty patient_ids list
    mode = "3D"

    with pytest.raises(ValueError, match="The patient_ids list cannot be empty."):
        get_patient_image_mask_dict(imgs_path, masks_path, patient_ids, mode)


def test_get_patient_image_mask_dict_images_masks_and_patient_ids_count():
    """
    GIVEN: Lists of image paths, mask paths, and patient ids with unequal lengths.
    WHEN: The get_patient_image_mask_dict function is called.
    THEN: The function should raise a ValueError indicating that the number of images, masks, and patient_ids must be the same.
    """
    imgs_path = ["img1.nii", "img2.nii"]
    masks_path = ["mask1.nii"]
    patient_ids = [1, 2]
    mode = "3D"

    with pytest.raises(ValueError, match="The number of images, masks, and patient_ids must be the same."):
        get_patient_image_mask_dict(imgs_path, masks_path, patient_ids, mode)


from unittest.mock import patch


@patch('image_processing.read_image_and_mask')
def test_get_patient_image_mask_dict_invalid_mode(mock_read_image):
    # Simula il comportamento della funzione
    mock_read_image.return_value = (None, None)  # Simuliamo un ritorno fittizio da `read_image_and_mask`

    imgs_path = ["img1.nii", "img2.nii"]
    masks_path = ["mask1.nii", "mask2.nii"]
    patient_ids = [1, 2]
    mode = "4D"  # Invalid mode

    with pytest.raises(ValueError, match="Mode should be '2D' or '3D'"):
        get_patient_image_mask_dict(imgs_path, masks_path, patient_ids, mode)


@pytest.fixture
def mock_read_image_and_mask():
    """Mock function to replace read_image_and_mask."""

    def _mock(img_path, mask_path):
        img = sitk.Image(3, 3, 3, sitk.sitkUInt8)
        mask = sitk.Image(3, 3, 3, sitk.sitkUInt8)
        return img, mask

    return _mock


@pytest.fixture
def sample_data():
    """Fixture providing sample input data."""
    return {
        "imgs_path": ["img1.nii", "img2.nii"],
        "masks_path": ["mask1.nii", "mask2.nii"],
        "patient_ids": [1, 2],
        "mode": "3D",
    }


def test_get_patient_image_mask_dict_type(monkeypatch, mock_read_image_and_mask, sample_data):
    """Check if the function returns a dictionary."""
    monkeypatch.setattr("image_processing.read_image_and_mask", mock_read_image_and_mask)

    result = get_patient_image_mask_dict(**sample_data)

    assert isinstance(result, dict), f"Expected a dictionary, but got {type(result)}"

def test_get_patient_image_mask_dict_patient_count(monkeypatch, mock_read_image_and_mask, sample_data):
    """Check if the function returns the correct number of patients."""
    monkeypatch.setattr("image_processing.read_image_and_mask", mock_read_image_and_mask)

    result = get_patient_image_mask_dict(**sample_data)

    assert len(result) == 2, f"Expected 2 patients, but got {len(result)}"


def test_get_patient_image_mask_dict_3D_mask_type(monkeypatch, mock_read_image_and_mask, sample_data):
    """
    GIVEN: A valid list of 3D images and masks with patient IDs.
    WHEN: The function is called in 3D mode.
    THEN: The masks in the output dictionary should be instances of SimpleITK Image.
    """
    monkeypatch.setattr("image_processing.read_image_and_mask", mock_read_image_and_mask)

    result = get_patient_image_mask_dict(**sample_data)

    for patient_id in sample_data["patient_ids"]:
        assert isinstance(result[patient_id][0]['MaskVolume'], sitk.Image), "Mask should be a SimpleITK image."


def test_get_patient_image_mask_dict_3D_mask_dimension(monkeypatch, mock_read_image_and_mask, sample_data):
    """
    GIVEN: A valid list of 3D images and masks with patient IDs.
    WHEN: The function is called in 3D mode.
    THEN: The masks in the output dictionary should have 3 dimensions.
    """
    monkeypatch.setattr("image_processing.read_image_and_mask", mock_read_image_and_mask)

    result = get_patient_image_mask_dict(**sample_data)

    for patient_id in sample_data["patient_ids"]:
        assert result[patient_id][0]['MaskVolume'].GetDimension() == 3, "Mask should be 3D in 3D mode."

def test_get_patient_image_mask_dict_3D_img_type(monkeypatch, mock_read_image_and_mask, sample_data):
    """
    GIVEN: A valid list of 3D images and masks with patient IDs.
    WHEN: The function is called in 3D mode.
    THEN: The image in the output dictionary should be instances of SimpleITK Image.
    """
    monkeypatch.setattr("image_processing.read_image_and_mask", mock_read_image_and_mask)

    result = get_patient_image_mask_dict(**sample_data)

    for patient_id in sample_data["patient_ids"]:
        assert isinstance(result[patient_id][0]['ImageVolume'], sitk.Image), "Image should be a SimpleITK image."


def test_get_patient_image_mask_dict_3D_img_dimension(monkeypatch, mock_read_image_and_mask, sample_data):
    """
    GIVEN: A valid list of 3D images and masks with patient IDs.
    WHEN: The function is called in 3D mode.
    THEN: The image in the output dictionary should have 3 dimensions.
    """
    monkeypatch.setattr("image_processing.read_image_and_mask", mock_read_image_and_mask)

    result = get_patient_image_mask_dict(**sample_data)

    for patient_id in sample_data["patient_ids"]:
        assert result[patient_id][0]['ImageVolume'].GetDimension() == 3, "Image should be 3D in 3D mode."


def test_read_image_and_mask_empty_path():
    """
    GIVEN: Empty paths for image and mask.
    WHEN: The function is called.
    THEN: It should raise a ValueError.
    """
    with pytest.raises(ValueError, match="Image and mask paths cannot be empty."):
        read_image_and_mask("", "")


def test_read_image_and_mask_non_string_path():
    """
    GIVEN: Non-string paths for image and mask.
    WHEN: The function is called.
    THEN: It should raise a TypeError.
    """
    with pytest.raises(TypeError, match="Image and mask paths must be strings."):
        read_image_and_mask(123, 456)


@pytest.fixture
def mock_read_image_and_mask_different_size():
    """Mock function to return an image and a mask with different dimensions."""
    def _mock(img_path, mask_path):
        img = sitk.Image(3, 3, 3, sitk.sitkUInt8)  # 3x3x3 image
        mask = sitk.Image(4, 4, 4, sitk.sitkUInt8)  # 4x4x4 mask (different size)
        return img, mask

    return _mock


def test_read_image_and_mask_dimension_mismatch(mock_read_image_and_mask_different_size, monkeypatch):
    """
    GIVEN: Image and mask with different dimensions.
    WHEN: The function is called.
    THEN: It should raise a ValueError.
    """
    monkeypatch.setattr("SimpleITK.ReadImage",
                        lambda path: mock_read_image_and_mask_different_size(path, path)[0 if "image" in path else 1])

    with pytest.raises(ValueError, match="Image and mask dimensions do not match."):
        read_image_and_mask("image.nii", "mask.nii")
