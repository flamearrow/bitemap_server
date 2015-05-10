# get img files
items := $(shell ls *.* | grep -E '*.[j][pP][gG]|*.[J][pP][gG]|*.[Pp][Nn][gG]|*.[Jj][pP][nN][gG]')
thumbs := $(addprefix thumb/,$(items))
reduced := $(addprefix reduced/,$(items))

all: $(thumbs) $(reduced) list 

# generate thumbs
$(thumbs): thumb/%: %
	[ ! -d 'thumb' ] && mkdir thumb;\
	convert -resize 192x128\> $< $@

# generate thumbs
$(reduced): reduced/%: %
	[ ! -d 'reduced' ] && mkdir reduced;\
	convert -resize 700x700\> $< $@

.PHONY: list clean


# generate thumb list
list: 
	echo 'imgs:' > list.yml;\
	for item in $(items); do\
        	echo -e '\t- '$$item >> list.yml;\
	done;\

# clean redundant thumbs
clean:
	ls thumb | grep -E '*.*' | xargs -l -i rm thumb/{};
	ls reduced | grep -E '*.*' | xargs -l -i rm reduced/{};
	rm truck.php

# clean all thumbs
clean-all:
	rm -rf file thumb reduced list.yml
