import React, { useState } from "react";
import axios from "axios";

const ImageConcatenator = () => {
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [orientation, setOrientation] = useState("horizontal");
  const [combinedImage, setCombinedImage] = useState(null);

  const handleImageChange = (e, setImage) => {
    const file = e.target.files[0];
    if (file) setImage(file);
  };

  const handleConcatenate = async () => {
    if (!image1 || !image2) {
      alert("Please upload both images");
      return;
    }

    const formData = new FormData();
    formData.append("image1", image1);
    formData.append("image2", image2);
    formData.append("orientation", orientation);

    try {
      const response = await axios.post(
        "http://localhost:5000/concatenate-images",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setCombinedImage(`data:image/png;base64,${response.data.combined_image}`);
    } catch (error) {
      console.error("Error concatenating images:", error);
      console.log(error);
      alert("Failed to concatenate images.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">
      <h1 className="text-2xl font-bold mb-4">Image Concatenator</h1>
      <div className="flex gap-4 mb-4">
        {/* Image Upload */}
        <div className="flex flex-col items-center">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleImageChange(e, setImage1)}
          />
          <p className="text-gray-600">Upload First Image</p>
        </div>
        <div className="flex flex-col items-center">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleImageChange(e, setImage2)}
          />
          <p className="text-gray-600">Upload Second Image</p>
        </div>
      </div>

      {/* Drag-and-Drop Canvas */}
      <div className="w-96 h-96 border-2 border-dashed border-gray-300 bg-white mb-4 flex justify-center items-center">
        <p className="text-gray-500">
          Drag and drop images here (Mockup Placeholder)
        </p>
      </div>

      {/* Orientation Selector */}
      <div className="mb-4">
        <label className="mr-2">
          <input
            type="radio"
            value="horizontal"
            checked={orientation === "horizontal"}
            onChange={(e) => setOrientation(e.target.value)}
          />
          Horizontal
        </label>
        <label className="ml-4">
          <input
            type="radio"
            value="vertical"
            checked={orientation === "vertical"}
            onChange={(e) => setOrientation(e.target.value)}
          />
          Vertical
        </label>
      </div>

      {/* Concatenate Button */}
      <button
        onClick={handleConcatenate}
        className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Concatenate Images
      </button>

      {/* Combined Image */}
      {combinedImage && (
        <div className="mt-6">
          <h2 className="text-lg font-bold mb-2">Combined Image:</h2>
          <img src={combinedImage} alt="Combined" className="max-w-full" />
          <a
            href={combinedImage}
            download="combined_image.png"
            className="mt-2 inline-block px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Download Image
          </a>
        </div>
      )}
    </div>
  );
};

export default ImageConcatenator;
