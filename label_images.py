import boto3
import io
import os

from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont


def show_custom_labels(model, bucket, photo, min_confidence, filename):

    client = boto3.client('rekognition')

    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket, photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image = Image.open(stream)

    # Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                           MinConfidence=min_confidence,
                                           ProjectVersionArn=model)

    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            draw.text((left, top), customLabel['Name'], fill='#00d400')

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top))
            # can change the line color code and width
            draw.line(points, fill='#00d400', width=20)

    # image.show()
    image.save("{}".format(filename))
    return len(response['CustomLabels'])


def main():

    s3 = boto3.client("s3")
    # replace bucket name
    bucket = "<your bucket name>"
    response = s3.list_objects_v2(
        Bucket=bucket,
        # replace bucket prefix (s3 folder name)
        Prefix='<your bucket prefix>',
        MaxKeys=10000)

    for i in response['Contents'][1:]:
        # print(i['Key'])
        # photo = "testall/IMG_ (305).JPG"
        photo = i['Key']
        # replace model arn
        model = '<your arn>'
        min_confidence = 95
        label_count = show_custom_labels(
            model, bucket, photo, min_confidence, str(i['Key']))
        print("Custom labels detected: " + str(label_count))
        print("================================================")


if __name__ == "__main__":
    main()
