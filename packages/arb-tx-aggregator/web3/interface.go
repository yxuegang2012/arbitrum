package web3

import (
	"encoding/json"
	"fmt"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/core/types"
	ethrpc "github.com/ethereum/go-ethereum/rpc"
	"math/big"
)

type BlockNumberArgs struct{}

type AccountInfoArgs struct {
	Address  *common.Address
	BlockNum ethrpc.BlockNumber
}

func (n *AccountInfoArgs) UnmarshalJSON(buf []byte) error {
	return unmarshalJSONArray(buf, []interface{}{&n.Address, &n.BlockNum})
}

type GetBlockByNumberArgs struct {
	BlockNum      *ethrpc.BlockNumber
	IncludeTxData bool
}

func (n *GetBlockByNumberArgs) UnmarshalJSON(buf []byte) error {
	return unmarshalJSONArray(buf, []interface{}{&n.BlockNum, &n.IncludeTxData})
}

type GetBlockResult struct {
	types.Header
}

type CallTxArgs struct {
	From     *common.Address `json:"from"`
	To       *common.Address `json:"to"`
	Gas      *hexutil.Uint64 `json:"gas"`
	GasPrice *hexutil.Big    `json:"gasPrice"`
	Value    *hexutil.Big    `json:"value"`
	Data     *hexutil.Bytes  `json:"data"`
}

type CallArgs struct {
	CallArgs *CallTxArgs
	BlockNum *ethrpc.BlockNumber
}

func (n *CallArgs) UnmarshalJSON(buf []byte) error {
	return unmarshalJSONArray(buf, []interface{}{&n.CallArgs, &n.BlockNum})
}

type EmptyArgs struct{}

type SendTransactionArgs struct {
	Data *hexutil.Bytes
}

func (n *SendTransactionArgs) UnmarshalJSON(buf []byte) error {
	return unmarshalJSONArray(buf, []interface{}{&n.Data})
}

type GetTransactionReceiptArgs struct {
	Data *hexutil.Bytes
}

func (n *GetTransactionReceiptArgs) UnmarshalJSON(buf []byte) error {
	return unmarshalJSONArray(buf, []interface{}{&n.Data})
}

// Receipt represents the results of a transaction.
type GetTransactionReceiptResult struct {
	Status            uint64       `json:"status"`
	CumulativeGasUsed uint64       `json:"cumulativeGasUsed"`
	Bloom             string       `json:"logsBloom"`
	Logs              []*types.Log `json:"logs"`
	// They are stored in the chain database.
	TxHash          common.Hash `json:"transactionHash"`
	ContractAddress string      `json:"contractAddress"`
	GasUsed         uint64      `json:"gasUsed"`

	// Inclusion information: These fields provide information about the inclusion of the
	// transaction corresponding to this receipt.
	BlockHash        common.Hash `json:"blockHash"`
	BlockNumber      *big.Int    `json:"blockNumber"`
	TransactionIndex uint        `json:"transactionIndex"`
}

func unmarshalJSONArray(buf []byte, fields []interface{}) error {
	wantLen := len(fields)
	if err := json.Unmarshal(buf, &fields); err != nil {
		return err
	}
	if g, e := len(fields), wantLen; g != e {
		return fmt.Errorf("wrong number of fields in CallArgs: %d != %d", g, e)
	}
	return nil
}
