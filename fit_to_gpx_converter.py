import os
import fitparse
import gpxpy
import gpxpy.gpx
from xml.etree.ElementTree import Element


def convert_fit_to_gpx(fit_file, output_dir):
    """
    Converts a .fit file into a .gpx file and saves it to the output directory.

    :param fit_file: Path to the .fit file
    :param output_dir: Directory where the .gpx file will be saved
    """
    # Parse the .fit file
    fitfile = fitparse.FitFile(fit_file)

    # Create a new GPX file
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    records = list(fitfile.get_messages('record'))
    print(f"Number of records in {fit_file}: {len(records)}")

    for record in records:
        latitude = None
        longitude = None
        elevation = None
        time = None
        heart_rate = None

        for data in record:
            if data.value is None:
                continue
            if data.name == 'position_lat':
                latitude = data.value * (180 / 2 ** 31)  # Convert to degrees
            elif data.name == 'position_long':
                longitude = data.value * (180 / 2 ** 31)  # Convert to degrees
            elif data.name == 'altitude':
                elevation = data.value
            elif data.name == 'timestamp':
                time = data.value
            elif data.name == 'heart_rate':
                heart_rate = data.value

        # If a position is available, add it to the GPX track
        if latitude is not None and longitude is not None:
            gpx_point = gpxpy.gpx.GPXTrackPoint(
                latitude=latitude,
                longitude=longitude,
                elevation=elevation,
                time=time
            )

            # Add heart rate if it is available
            if heart_rate is not None:
                heart_rate_element = Element("heart_rate")
                heart_rate_element.text = str(heart_rate)
                gpx_point.extensions.append(heart_rate_element)

            gpx_segment.points.append(gpx_point)

    output_file = os.path.join(output_dir, os.path.basename(fit_file).replace('.fit', '.gpx'))
    with open(output_file, 'w') as gpx_file:
        gpx_file.write(gpx.to_xml())
    print(f"Successfully converted: {fit_file} -> {output_file}")


if __name__ == "__main__":
    # Input directory containing .fit files
    input_dir = "fit_files"  # Adjust this path as needed
    output_dir = "gpx_files"  # Adjust this path as needed

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process all .fit files in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith('.fit'):
            fit_file = os.path.join(input_dir, file_name)
            convert_fit_to_gpx(fit_file, output_dir)
