# pi-coin-scanner
Raspberry Pi image scanning script. A button calls the scanner to obtain the image. A self-locking button switches between naive document scanning and multiple coin/ingot scanning.

# Work flow for multiple coin/ingot scanning

1. Engage Raspberry Pi self-locking button.
2. Press Raspberry Pi button.
3. Scanner obtains image of the obverse of one or more coins/ingots laid out on the scan bed, and stores them on an NFS drive as one raw TIFF image.
4. After flipping coins/ingots, press Raspberry Pi button again.
5. Scanner obtains image of the reverse of one or more coins/ingots laid out on the scan bed, and stores them on an NFS drive as one raw TIFF image.
6. Raspberry Pi signals to remote server to begin splitting and merging the two corresponding images.
7. Remote server receives signal with image path and image names.
8. Remote server calls splitting and merging script.
9. Store merged images on NFS drive.
