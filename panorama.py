import cv2
import os
import numpy as np
import glob
import gc

# Disable OpenCL to force CPU processing
cv2.ocl.setUseOpenCL(False)

def extract_frames(video_path, output_dir, frame_interval=35):
    """
    Extract frames from a video file and save them to the output directory.
    
    Args:
        video_path (str): Path to the input video file
        output_dir (str): Directory to save the extracted frames
        frame_interval (int): Extract one frame every N frames (default: 35)
    """
    # Clear the output directory if it exists
    if os.path.exists(output_dir):
        # Remove all files in the directory
        files = glob.glob(os.path.join(output_dir, '*'))
        for f in files:
            os.remove(f)
        print(f"Cleared {len(files)} existing files from {output_dir}")
    else:
        # Create the directory if it doesn't exist
        os.makedirs(output_dir)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    frame_count = 0
    saved_frame_count = 0
    
    while True:
        # Read a frame from the video
        ret, frame = cap.read()
        
        # If frame is not read successfully, break the loop
        if not ret:
            break
        
        # Save frame at specified intervals
        if frame_count % frame_interval == 0:
            # Force rotate the frame 90 degrees clockwise
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            
            frame_path = os.path.join(output_dir, f"frame_{saved_frame_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_frame_count += 1
            print(f"Saved frame {saved_frame_count}")
        
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Extracted {saved_frame_count} frames from the video")
    return saved_frame_count

def create_panorama(input_dir, output_path):
    """
    Create a panorama image from a set of frames using OpenCV's Stitcher.
    
    Args:
        input_dir (str): Directory containing the frames
        output_path (str): Path to save the panorama image
    """
    # Get all image files from the input directory
    image_files = sorted(glob.glob(os.path.join(input_dir, '*.jpg')))
    
    if not image_files:
        print("No images found in the input directory")
        return
    
    # Limit to a reasonable number of images
    max_images = 28
    if len(image_files) > max_images:
        print(f"Limiting to {max_images} images to avoid memory issues")
        image_files = image_files[:max_images]
    
    print(f"Processing {len(image_files)} images")
    
    # Read all images
    images = []
    for img_path in image_files:
        img = cv2.imread(img_path)
        if img is not None:
            images.append(img)
    
    if not images:
        print("No valid images found")
        return
    
    print("Starting panorama creation...")
    
    try:
        # Create a stitcher
        stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
        
        # Try to stitch the images
        status, panorama = stitcher.stitch(images)
        
        if status == cv2.Stitcher_OK:
            # Save the panorama
            cv2.imwrite(output_path, panorama)
            print(f"Panorama successfully created and saved to {output_path}")
        else:
            print(f"Stitching failed with status: {status}")
            if status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
                print("Need more images to create a panorama")
            elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
                print("Failed to estimate homography")
            elif status == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
                print("Failed to adjust camera parameters")
    except Exception as e:
        print(f"Error during stitching: {e}")
        print("Trying to process fewer images...")
        
        # Try with fewer images
        if len(images) > 10:
            print("Retrying with 10 images")
            return create_panorama(input_dir, output_path, max_images=10)
        else:
            print("Failed to create panorama with any number of images")

if __name__ == "__main__":
    # Get all MP4 files from the input directory
    input_dir = "input"
    output_dir = "output"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all MP4 files
    video_files = glob.glob(os.path.join(input_dir, "*.mp4"))
    
    if not video_files:
        print("No MP4 files found in the input directory")
        exit()
    
    print(f"Found {len(video_files)} MP4 files to process")
    
    # Process each video file
    for video_path in video_files:
        # Get the base name of the video file
        video_name = os.path.basename(video_path)
        print(f"\nProcessing video: {video_name}")
        
        # Create a directory for this video's frames
        frames_dir = os.path.join("key_frames", video_name.split('.')[0])
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
        
        # Extract frames from the video
        num_frames = extract_frames(video_path, frames_dir)
        
        # Create panorama if we have enough frames
        if num_frames > 1:
            # Create output path for this video's panorama
            panorama_name = f"panorama_{video_name.split('.')[0]}.jpg"
            panorama_path = os.path.join(output_dir, panorama_name)
            
            # Create the panorama
            create_panorama(frames_dir, panorama_path)
            
            # Clean up the frames directory
            files = glob.glob(os.path.join(frames_dir, '*'))
            for f in files:
                os.remove(f)
            os.rmdir(frames_dir)
