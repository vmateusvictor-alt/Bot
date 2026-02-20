def split_into_volumes(chapters, size=50):
    volumes = []
    for i in range(0, len(chapters), size):
        volumes.append(chapters[i:i+size])
    return volumes
