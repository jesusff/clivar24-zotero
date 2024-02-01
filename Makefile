default:
	@echo "Try 'make update' or 'make backup'"

update:
	python common.py
	python tag-table.py
	python reports.py
	scp docs/*.html ui:/lustre/gmeteo/WORK/WWW/InformeCLIVAR24ch5/

clean:
	rm docs/report-*.html
	rm docs/tag-table-*.html

update-all: clean update

backup:
	python zotero_to_json.py
