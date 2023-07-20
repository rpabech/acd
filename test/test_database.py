from typing import List

import pytest

from acd.comps import CompsRecord
from acd.dbextract import DbExtract
from acd.export_l5x import ExportL5x
from acd.sbregion import SbRegionRecord
from acd.unzip import Unzip


@pytest.fixture()
async def sample_acd():
    unzip = Unzip("resources/CuteLogix.ACD").write_files("build")
    yield unzip


@pytest.fixture()
async def sbregion_dat():
    db = DbExtract("test/build/SbRegion.Dat")
    yield db


@pytest.fixture()
async def comps_dat():
    db = DbExtract("test/build/Comps.Dat")
    yield db

@pytest.fixture()
async def controller():
    yield ExportL5x("resources/CuteLogix.ACD", "test/build/output.txt").controller


def test_open_file(sample_acd, sbregion_dat):
    assert sbregion_dat


def test_header(sample_acd, sbregion_dat):
    assert sbregion_dat.header.pointer_records_region == 2591


def test_parse_rungs_dat(controller):
    rung = controller.programs[-1].routines[-1].rungs[-1]
    assert rung == 'FSC(FSCControl,?,?,ALL,Misc[2]=Misc[3])FSC(FSCControl,?,?,INC,Misc[2]=Misc[3]);'


def test_parse_datatypes_dat(controller):
    data_type = controller.data_types[-1].name
    child =  controller.data_types[-1].children[-1]
    assert data_type == 'STRING20'
    assert child == 'DATA'


def test_parse_tags_dat(controller):
    tag_name = controller.tags[75].text
    data_type =  controller.tags[75].data_type
    assert data_type == 'BOOL'
    assert tag_name == 'Toggle'

def test_parse_comments_dat():
    db: DbExtract = DbExtract("test/build/Comments.Dat")


def test_parse_nameless_dat():
    db: DbExtract = DbExtract("test/build/Nameless.Dat")
