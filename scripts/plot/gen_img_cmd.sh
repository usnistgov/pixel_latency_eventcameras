DIR=$1
EXEC_DIR=../plot/

all() {
    file=$1
    $EXEC_DIR/gen_figures_all.sh "$DIR/$file"
    mv "$DIR/${file}_result" "img/$DIR"
}

roi() {
    file=$1
    $EXEC_DIR/gen_figures_ROI.sh "$DIR/$file"
    mv "$DIR/${file}_ROI_result" "img/$DIR"
}

maps() {
    file=$1
    $EXEC_DIR/gen_figures_maps.sh "$DIR/$file"
    mv "$DIR/${file}_maps_result" "img/$DIR"
}

size_roi() {
    file=$1
    $EXEC_DIR/gen_figures_size_ROI.sh "$DIR/$file"
    mv "$DIR/${file}_size_roi_result" "img/$DIR"
}

# generate image for non ROI measurements
for file in $(ls $DIR | grep -E -v "roi|_result$"); do
    mkdir -p "img/$DIR/"
    all $file &
    roi $file &
    maps $file &
done

# generate image for ROI measurements
for file in $(ls $DIR | grep roi | grep -E -v "_result$"); do
    mkdir -p "img/$DIR/"
    size_roi $file &
done
