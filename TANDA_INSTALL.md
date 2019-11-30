In order to setup this package to use TANDA, run the following:
git checkout f3386d938348628c91457fc7d8650c223317a053 -b tanda-sequential-finetuning
git clone https://github.com/alexa/wqa_tanda
cd wqa_tanda 
mv tanda-sequential-finetuning-with-asnq.diff ..
cd ..
git apply tanda-sequential-finetuning-with-asnq.diff
pip install -r requirements-dev.txt
pip install future
pip install --editable .

