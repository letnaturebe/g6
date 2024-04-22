"""전체검색 API Router"""
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from api.v1.models.response import response_401, response_403, response_422
from api.v1.models.board import ResponseBoardModel, ResponseWriteSearchModel, ResponseSearchModel
from service.search import SearchServiceAPI

router = APIRouter()


@router.get("/search",
            summary="게시판 검색",
            responses={**response_401, **response_403, **response_422}
            )
async def api_search(
    search_service: Annotated[SearchServiceAPI, Depends()],
    sfl: str = Query("wr_subject||wr_content", title="검색필드", description="검색필드"),
    stx: str = Query(..., title="검색어", description="검색어"),
    sop: str = Query("and", title="검색연산자", description="검색연산자", pattern="and|or"),
    onetable: str = Query(None, title="통합검색", description="통합검색"),
) -> ResponseSearchModel:
    """
    게시판 검색
    - 게시판 종류와, 개별 게시판에 있는 게시글을 검색합니다.
    """
    boards = search_service.get_boards()
    searched_result = search_service.search(boards, sfl, stx, sop)
    total_search_count = searched_result["total_search_count"]
    boards = searched_result["boards"]

    # board 및 write에 대해 지정해준 API 속성만 필터링
    filtered_boards = []
    for board in boards:
        board_json = jsonable_encoder(board)
        board_json_writes = board_json["writes"]
        filtered_writes = []
        for write in board_json_writes:
            write_api = ResponseWriteSearchModel.model_validate(write)
            filtered_writes.append(write_api)
        board_api = dict(ResponseBoardModel.model_validate(board_json))
        board_api["writes"] = filtered_writes
        filtered_boards.append(board_api)

    return {
        "onetable": onetable,
        "total_search_count": total_search_count,
        "boards": filtered_boards,
    }
