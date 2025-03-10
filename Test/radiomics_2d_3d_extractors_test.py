import logging
import pytest
from radiomics import featureextractor
from radiomics_2d_3d_extractors import *
import numpy as np
import SimpleITK as sitk
from unittest.mock import Mock


def test_get_extractor_invalid_type():
    """
    GIVEN a non-string yaml_path
    WHEN get_extractor is called
    THEN it should raise a TypeError.
    """
    with pytest.raises(TypeError, match="yaml_path must be a string."):
        get_extractor(123)

def test_get_extractor_empty_string():
    """
    GIVEN an empty string as yaml_path
    WHEN get_extractor is called
    THEN it should raise a ValueError.
    """
    with pytest.raises(ValueError, match="yaml_path cannot be empty."):
        get_extractor("")

def test_get_extractor_file_not_found():
    """
    GIVEN a non-existent file path
    WHEN get_extractor is called
    THEN it should raise a FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError, match="The file 'non_existent.yaml' does not exist."):
        get_extractor("non_existent.yaml")


def test_radiomic_extractor_3D_empty_labels():
    """
    GIVEN a patient_dict_3D with an empty mask (no labels)
    WHEN radiomic_extractor_3D is called with these inputs
    THEN it should raise a ValueError indicating no labels in the mask
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10, 10))
    mask_1 = sitk.GetImageFromArray(np.zeros((10, 10, 10)))

    # Mock patient_dict_3D with SimpleITK images
    patient_dict_3D = {
        123: [{"ImageVolume": img_1, "MaskVolume": mask_1}],
    }

    # Mock extractor object
    extractor = Mock()

    # Call the function under test and check for the raised error
    with pytest.raises(ValueError, match="No labels found in mask for patient 123"):
        radiomic_extractor_3D(patient_dict_3D, extractor)


def test_radiomic_extractor_3D_logging_error(caplog):
    """
    GIVEN a patient_dict_3D with a valid image and mask
    WHEN the extractor.execute method raises an exception
    THEN it should log an error message
    """
    # Mock data: image and mask with label 1
    img = sitk.GetImageFromArray(np.random.rand(10, 10, 10))
    mask = sitk.GetImageFromArray(np.full((10, 10, 10), fill_value=2, dtype=np.uint16))

    # Patient mock dictionary
    patient_dict_3D = {
        123: [{"ImageVolume": img, "MaskVolume": mask}],
    }

    # Mock extractor
    extractor = Mock()

    # extractor.execute raise an exception
    extractor.execute.side_effect = Exception("Test Exception")
    print(sitk.GetArrayFromImage(mask).dtype, sitk.GetArrayFromImage(mask).shape)


    # Takes log
    with caplog.at_level(logging.ERROR):
        result = radiomic_extractor_3D(patient_dict_3D, extractor)

    # Verify that the log contains the expected error message
    assert any(
        "[Invalid Feature] for patient PR123, label 2: Test Exception" in record.message for record in caplog.records)


def test_radiomic_extractor_3D_valid_input_patient_key():
    """
    GIVEN a valid patient_dict_3D and extractor
    WHEN radiomic_extractor_3D is called with these valid inputs
    THEN it should return a dictionary with the expected patient key
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10, 10))
    mask_1 = sitk.GetImageFromArray(np.full((10, 10, 10), fill_value=1, dtype=np.uint16))  # Assuming this will result in a label of 1

    # Mock patient_dict_3D with SimpleITK images
    patient_dict_3D = {
        "123": [{"ImageVolume": img_1, "MaskVolume": mask_1}],
    }

    # Mock extractor object
    extractor = Mock()
    extractor.execute.return_value = {"Feature1": 0.5, "Feature2": 0.8}

    # Call the function under test
    result = radiomic_extractor_3D(patient_dict_3D, extractor)

    # Check that the result contains the expected patient key
    assert "PR123 - 1" in result


def test_radiomic_extractor_3D_valid_input_feature1():
    """
    GIVEN a valid patient_dict_3D and extractor
    WHEN radiomic_extractor_3D is called with these valid inputs
    THEN it should return the correct value for Feature1
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10, 10))
    mask_1 = sitk.GetImageFromArray(np.full((10, 10, 10), fill_value=1, dtype=np.uint16))  # Assuming this will result in a label of 1

    # Mock patient_dict_3D with SimpleITK images
    patient_dict_3D = {
        "123": [{"ImageVolume": img_1, "MaskVolume": mask_1}],
    }

    # Mock extractor object
    extractor = Mock()
    extractor.execute.return_value = {"Feature1": 0.5, "Feature2": 0.8}

    # Call the function under test
    result = radiomic_extractor_3D(patient_dict_3D, extractor)

    # Check that the result contains the correct value for Feature1
    assert result["PR123 - 1"]["Feature1"] == 0.5


def test_radiomic_extractor_3D_valid_input_feature2():
    """
    GIVEN a valid patient_dict_3D and extractor
    WHEN radiomic_extractor_3D is called with these valid inputs
    THEN it should return the correct value for Feature2
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10, 10))
    mask_1 = sitk.GetImageFromArray(np.full((10, 10, 10), fill_value=1, dtype=np.uint16))  # Assuming this will result in a label of 1

    # Mock patient_dict_3D with SimpleITK images
    patient_dict_3D = {
        "123": [{"ImageVolume": img_1, "MaskVolume": mask_1}],
    }

    # Mock extractor object
    extractor = Mock()
    extractor.execute.return_value = {"Feature1": 0.5, "Feature2": 0.8}

    # Call the function under test
    result = radiomic_extractor_3D(patient_dict_3D, extractor)

    # Check that the result contains the correct value for Feature2
    assert result["PR123 - 1"]["Feature2"] == 0.8



def test_radiomic_extractor_2D_empty_labels():
    """
    GIVEN a patient_dict_2D with an empty mask (no labels)
    WHEN radiomic_extractor_2D is called with these inputs
    THEN it should raise a ValueError indicating no labels in the mask
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10, 10))
    mask_1 = sitk.GetImageFromArray(np.zeros((10, 10, 10)))

    # Mock patient_dict_2D with SimpleITK images
    patient_dict_2D = {
        123: [{"ImageSlice": img_1, "MaskSlice": mask_1, "Label": 0, "SliceIndex": 0}],
    }

    # Mock extractor object
    extractor = Mock()

    # Call the function under test and check for the raised error
    with pytest.raises(ValueError, match="No labels found in mask for patient 123"):
        radiomic_extractor_2D(patient_dict_2D, extractor)


def test_radiomic_extractor_2D_logging_error(caplog):
    """
    GIVEN a patient_dict_2D with a valid image and mask
    WHEN the extractor.execute method raises an exception
    THEN it should log an error message
    """
    # Create mock 2D image and mask
    img = sitk.GetImageFromArray(np.random.rand(10, 10))
    mask = sitk.GetImageFromArray(np.full((10, 10), fill_value=2, dtype=np.uint16))  # Assuming label 2

    # Patient mock dictionary
    patient_dict_2D = {
        123: [{"ImageSlice": img, "MaskSlice": mask, "Label": 2, "SliceIndex": 0}],
    }

    # Mock extractor
    extractor = Mock()
    # Make the extractor raise an exception
    extractor.execute.side_effect = Exception("Test Exception")

    # Capture logs
    with caplog.at_level(logging.ERROR):
        result = radiomic_extractor_2D(patient_dict_2D, extractor)

    # Verify that the error log contains the expected message
    assert any(
        "[Invalid Feature] for patient 123, Slice 0, Label 2: Test Exception" in record.message for record in caplog.records
    )


def test_radiomic_extractor_2D_valid_input_patient_key():
    """
    GIVEN a valid patient_dict_2D and extractor
    WHEN radiomic_extractor_2D is called with these valid inputs
    THEN it should return a dictionary with the expected patient key
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10))
    mask_1 = sitk.GetImageFromArray(np.full((10, 10), fill_value=1, dtype=np.uint16))  # Label 1

    # Mock patient_dict_2D with SimpleITK images
    patient_dict_2D = {
        123: [{"ImageSlice": img_1, "MaskSlice": mask_1, "Label": 1, "SliceIndex": 0}],
    }

    # Mock extractor object
    extractor = Mock()
    extractor.execute.return_value = {"Feature1": 0.5, "Feature2": 0.8}

    # Call the function under test
    result = radiomic_extractor_2D(patient_dict_2D, extractor)

    # Check that the result contains the expected patient key
    assert "123-0-1" in result


def test_radiomic_extractor_2D_valid_input_feature1():
    """
    GIVEN a valid patient_dict_2D and extractor
    WHEN radiomic_extractor_2D is called with these valid inputs
    THEN it should return the correct value for Feature1
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10))
    mask_1 = sitk.GetImageFromArray(np.full((10, 10), fill_value=1, dtype=np.uint16))  # Label 1

    # Mock patient_dict_2D with SimpleITK images
    patient_dict_2D = {
        123: [{"ImageSlice": img_1, "MaskSlice": mask_1, "Label": 1, "SliceIndex": 0}],
    }

    # Mock extractor object
    extractor = Mock()
    extractor.execute.return_value = {"Feature1": 0.5, "Feature2": 0.8}

    # Call the function under test
    result = radiomic_extractor_2D(patient_dict_2D, extractor)

    # Check that the result contains the correct value for Feature1
    assert result["123-0-1"]["Feature1"] == 0.5


def test_radiomic_extractor_2D_valid_input_feature2():
    """
    GIVEN a valid patient_dict_2D and extractor
    WHEN radiomic_extractor_2D is called with these valid inputs
    THEN it should return the correct value for Feature2
    """
    # Mock data for the patient (SimpleITK Image objects)
    img_1 = sitk.GetImageFromArray(np.random.rand(10, 10))
    mask_1 = sitk.GetImageFromArray(np.full((10, 10), fill_value=1, dtype=np.uint16))  # Label 1

    # Mock patient_dict_2D with SimpleITK images
    patient_dict_2D = {
        123: [{"ImageSlice": img_1, "MaskSlice": mask_1, "Label": 1, "SliceIndex": 0}],
    }

    # Mock extractor object
    extractor = Mock()
    extractor.execute.return_value = {"Feature1": 0.5, "Feature2": 0.8}

    # Call the function under test
    result = radiomic_extractor_2D(patient_dict_2D, extractor)

    # Check that the result contains the correct value for Feature2
    assert result["123-0-1"]["Feature2"] == 0.8


# Dummy extractor for testing purposes
class DummyExtractor:
    def execute(self, patient_dict):
        return {"feature1": 1.0, "feature2": 2.0}


def test_extract_radiomic_features_patient_dict_not_dict():
    """
    Testing that a TypeError is raised when patient_dict is not a dictionary

    GIVEN patient_dict is not a dictionary
    WHEN calling extract_radiomic_features
    THEN it should raise a TypeError with the message 'patient_dict must be a dictionary.'
    """
    patient_dict = ["invalid_patient_data"]
    extractor = DummyExtractor()
    with pytest.raises(TypeError, match="patient_dict must be a dictionary."):
        extract_radiomic_features(patient_dict, extractor, mode="3D")


def test_extract_radiomic_features_invalid_mode():
    """
    Testing that a ValueError is raised when an invalid mode is provided

    GIVEN an invalid mode (not '2D' or '3D')
    WHEN calling extract_radiomic_features
    THEN it should raise a ValueError with the message 'Invalid mode. Choose either '2D' or '3D'.'
    """
    patient_dict = {"patient_id": 1, "image_data": "some_data"}
    extractor = DummyExtractor()
    with pytest.raises(ValueError, match="Invalid mode. Choose either '2D' or '3D'."):
        extract_radiomic_features(patient_dict, extractor, mode="invalid_mode")


def test_extract_radiomic_features_extractor_not_configured():
    """
    Testing that a ValueError is raised when the extractor is not configured properly

    GIVEN the extractor is not configured properly (lacking 'execute' method)
    WHEN calling extract_radiomic_features
    THEN it should raise a ValueError with the message 'Extractor is not configured properly. Ensure it has the necessary methods.'
    """

    class UnconfiguredExtractor:
        pass

    patient_dict = {"patient_id": 1, "image_data": "some_data"}
    extractor = UnconfiguredExtractor()
    with pytest.raises(ValueError, match="Extractor is not configured properly. Ensure it has the necessary methods."):
        extract_radiomic_features(patient_dict, extractor, mode="3D")
